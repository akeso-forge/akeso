"""
SCAN COMMAND
------------
Audits manifests for logical issues (read-only).
"""
import os
import sys
import json
import time
from akeso.core.engine import AkesoEngine
from akeso.cli.commands.base import get_console
from akeso.ui.reporters import JSONReporter, SARIFReporter

def handle_scan_command(args, engine, formatter):
    """
    Handles 'scan' subcommand execution.
    """
    extensions = [e.strip() for e in args.ext.split(",")]
    
    # Scan implies dry-run heal
    is_dry = True 

    start_time = time.time()
    
    # Collect results
    if args.path == "-":
        # STDIN Mode
        content = sys.stdin.read()
        job_results = [engine.audit_stream(content, source_name="<stdin>")]
    elif os.path.isfile(args.path):
        result = engine.audit_and_heal_file(args.path, dry_run=is_dry)
        job_results = [result]
    else:
        job_results = engine.batch_heal(
            root_path=args.path, 
            extensions=extensions, 
            max_depth=args.max_depth,
            dry_run=is_dry
        )

    # Handle Output Formats
    output_fmt = getattr(args, 'output', 'text')
    
    if output_fmt in ["json", "sarif"]:
        # Prepare data for reporters
        duration = time.time() - start_time
        data = {
            "processed_files": job_results,
            "healed_count": sum(1 for r in job_results if r.get("written") or r.get("healed_content")),
            "success_count": sum(1 for r in job_results if r.get("success"))
        }

        if output_fmt == "json":
            print(JSONReporter().generate(data, duration))
        elif output_fmt == "sarif":
             print(SARIFReporter().generate(data))
             
    else:
        # Standard Text/Table Output
        if os.path.isfile(args.path):
             result = job_results[0]
             formatter.display_report(result)
             
             # Support --diff
             if getattr(args, 'diff', False):
                 from akeso.ui.diff import DiffEngine
                 if result.get("healed_content") and result.get("raw_content") != result.get("healed_content"):
                     DiffEngine.render_diff(
                        result.get("raw_content", ""), 
                        result.get("healed_content", ""), 
                        result.get("file_path", "Unknown")
                     )

        else:
             summary_mode = getattr(args, 'summary_only', False)
             formatter.print_final_table(job_results, summary_only=summary_mode)
             
             # Support --diff for Batch Scan
             if getattr(args, 'diff', False):
                 from akeso.ui.diff import DiffEngine
                 console = get_console()
                 changed_jobs = [j for j in job_results if j.get("healed_content") and j.get("raw_content") != j.get("healed_content")]
                 
                 if changed_jobs:
                    console.print(f"\n[bold yellow]Found {len(changed_jobs)} files with proposed repairs:[/bold yellow]")
                    for job in changed_jobs:
                        DiffEngine.render_diff(
                            job.get("raw_content", ""), 
                            job.get("healed_content", ""), 
                            job.get("file_path", "Unknown")
                        )
                 else:
                    if not summary_mode: # Don't double print if table shows it
                        console.print("\n[green]No changes proposed (files are healthy).[/green]")
            
    # Calculate Exit Code
    # Fail if any file didn't meet threshold OR if changes are proposed
    # For CI/CD linter, we usually want to fail if there are any violations (i.e. if it *would* change)
    files_with_issues = [j for j in job_results if not j.get("success") or (j.get("healed_content") and j.get("raw_content") != j.get("healed_content"))]
    exit_code = 1 if files_with_issues else 0

    if exit_code != 0 and output_fmt == "text":
        console = get_console()
        if args.path != "-":
            console.print(f"\n[bold]💡 Tip:[/bold] Run [cyan]akeso heal {args.path}[/cyan] to fix {len(files_with_issues)} detected issues.\n")
        else:
            console.print(f"\n[bold yellow]⚠️  Found {len(files_with_issues)} issues in input stream.[/bold yellow]\n")

    return exit_code
