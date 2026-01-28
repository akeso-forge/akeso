"""
AKESO DIFF ENGINE
-----------------
Provides rich, colorful diffs for the CLI.
Supports:
- Side-by-side comparison (ideal for batch review)
- Inline diffs (classic git style)
- Syntax highlighting via Rich

Author: Nishar A Sunkesala / Akeso Team
Date: 2026-01-27
"""

import difflib
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
from rich.panel import Panel
from rich.text import Text

console = Console()

class DiffEngine:
    """Renders colorful diffs for Kubernetes manifests."""

    @staticmethod
    def render_diff(original: str, healed: str, file_path: str, side_by_side: bool = True):
        """
        Displays a diff between the original and healed content.
        
        Args:
            original: The raw content before healing.
            healed: The content after healing.
            file_path: Name of the file being modified.
            side_by_side: If True, uses a 2-column layout. False uses unified diff.
        """
        if original == healed:
            console.print(f"[dim]No changes for {file_path}[/dim]")
            return

        # Prepare title
        title = f":wrench: Proposed Changes for [bold cyan]{file_path}[/bold cyan]"
        
        if side_by_side:
            DiffEngine._render_side_by_side(original, healed, title)
        else:
            DiffEngine._render_inline(original, healed, title)

    @staticmethod
    def _render_side_by_side(original: str, healed: str, title: str):
        """Renders two panels side-by-side."""
        table = Table(title=title, show_header=True, header_style="bold magenta", expand=True, box=None)
        table.add_column("Original (Current)", style="dim red", ratio=1)
        table.add_column("Healed (Proposed)", style="green", ratio=1)

        # We construct the visual flow line by line using difflib
        # but for side-by-side, we might just show Syntax blocks if they aren't too big.
        # However, highlighting *changes* is tricky in side-by-side without line-matching logic.
        
        # Simpler approach V1: Show full blocks with syntax highlighting
        # This is easier to read for context than a fragmented diff.
        
        orig_syntax = Syntax(original, "yaml", line_numbers=True, theme="monokai")
        healed_syntax = Syntax(healed, "yaml", line_numbers=True, theme="monokai")
        
        table.add_row(orig_syntax, healed_syntax)
        console.print(table)
        console.print("[dim italic]Use arrows to scroll if content is long[/dim italic]\n")

    @staticmethod
    def _render_inline(original: str, healed: str, title: str):
        """Renders a standard unified diff with colors."""
        diff_lines = list(difflib.unified_diff(
            original.splitlines(keepends=True),
            healed.splitlines(keepends=True),
            fromfile="Original",
            tofile="Healed",
            n=3 # Context lines
        ))
        
        # Build a Rich Text object for the diff
        diff_text = Text()
        for line in diff_lines:
             if line.startswith("---") or line.startswith("+++"):
                 diff_text.append(line, style="bold magenta")
             elif line.startswith("@@"):
                 diff_text.append(line, style="cyan")
             elif line.startswith("-"):
                 diff_text.append(line, style="red")
             elif line.startswith("+"):
                 diff_text.append(line, style="green")
             else:
                 diff_text.append(line, style="dim white")
        
        console.print(Panel(diff_text, title=title, expand=False, border_style="blue"))
