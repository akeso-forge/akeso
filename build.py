#!/usr/bin/env python3
"""
AKESO BUILD SYSTEM (Cross-Platform)
-----------------------------------
Zero-config build script for Windows, Linux, and macOS.
Builds:
1. Standalone Binary (dist/akeso[.exe])
2. Kubecuro Alias (dist/kubecuro[.exe])

Future-Proofing:
- Auto-installs dependencies from pyproject.toml
- Auto-detects OS and path separators
- Dynamically includes all catalog/*.json files
"""

import sys
import os
import shutil
import subprocess
import glob
from pathlib import Path
import venv

# Configuration
APP_NAME = "akeso"
ALIAS_NAME = "kubecuro"
ENTRY_POINT = "src/akeso/cli/main.py"
BUILD_DIR = Path("build")
DIST_DIR = Path("dist")
VENV_DIR = Path(".venv_build")

def print_step(msg):
    print(f"\n\033[1;36m[BUILD] {msg}\033[0m")

def fail(msg):
    print(f"\n\033[1;31m[ERROR] {msg}\033[0m")
    sys.exit(1)

def run(cmd, env=None, cwd=None):
    """Runs a shell command and fails on error."""
    print(f"   $ {' '.join(cmd)}")
    try:
        subprocess.check_call(cmd, env=env, cwd=cwd)
    except subprocess.CalledProcessError:
        fail(f"Command failed: {' '.join(cmd)}")

def main():
    root_dir = Path(__file__).parent.resolve()
    os.chdir(root_dir)

    # 1. Cleanup
    print_step("Cleaning previous build artifacts...")
    if BUILD_DIR.exists(): shutil.rmtree(BUILD_DIR)
    if DIST_DIR.exists(): shutil.rmtree(DIST_DIR)
    for p in glob.glob("*.spec"): os.remove(p)

    # 2. Virtual Environment
    print_step(f"Setting up build environment in {VENV_DIR}...")
    if not VENV_DIR.exists():
        venv.create(VENV_DIR, with_pip=True)
    
    # Determine executables
    if sys.platform == "win32":
        python_exe = VENV_DIR / "Scripts" / "python.exe"
        pyinstaller_exe = VENV_DIR / "Scripts" / "pyinstaller.exe"
        bin_ext = ".exe"
        path_sep = ";"
    else:
        python_exe = VENV_DIR / "bin" / "python"
        pyinstaller_exe = VENV_DIR / "bin" / "pyinstaller"
        bin_ext = ""
        path_sep = ":"

    # 3. Install Dependencies
    print_step("Installing dependencies...")
    # Upgrade build tools safely via python -m pip
    run([str(python_exe), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel", "pyinstaller"])
    # Install project dependencies
    run([str(python_exe), "-m", "pip", "install", "."])

    # 4. Configure Assets
    # Dynamically find all catalog JSONs to include
    catalog_path = root_dir / "catalog"
    assets = []
    
    if catalog_path.exists():
        # Format: source_path:dest_path
        # We want catalog/* -> akeso/catalog/
        assets.append(f"{catalog_path}{path_sep}akeso/catalog")
        print(f"   + Included Catalog: {catalog_path}")
    
    # 5. Build Binary
    print_step(f"Compiling {APP_NAME}{bin_ext}...")
    
    cmd = [
        str(pyinstaller_exe),
        "--noconfirm",
        "--onefile",
        "--clean",
        "--name", APP_NAME,
        "--strip",  # Symbol stripping for smaller size
        "--paths", str(root_dir / "src"),
        # Hidden imports often missed by analysis
        "--hidden-import", "akeso.core.io",
        "--hidden-import", "akeso.core.pipeline",
        "--hidden-import", "akeso.analyzers.cross_resource",
        "--collect-all", "rich",
    ]
    
    for asset in assets:
        cmd.extend(["--add-data", asset])
        
    cmd.append(str(root_dir / ENTRY_POINT))
    
    run(cmd)

    # 6. Create Alias
    print_step(f"Creating alias {ALIAS_NAME}{bin_ext}...")
    src_bin = DIST_DIR / f"{APP_NAME}{bin_ext}"
    dest_bin = DIST_DIR / f"{ALIAS_NAME}{bin_ext}"
    
    shutil.copy2(src_bin, dest_bin)
    
    # 7. Verification
    print_step("Verifying build...")
    if not src_bin.exists():
        fail("Build failed - binary not found!")
        
    size_mb = src_bin.stat().st_size / (1024 * 1024)
    print(f"   ✅ Success! Binary size: {size_mb:.2f} MB")
    print(f"   📍 Artifacts: {src_bin} & {dest_bin}")

if __name__ == "__main__":
    main()
