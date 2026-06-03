#!/usr/bin/env python3
"""
Arctos Dashboard Update Tool — Setup Script

Run this script once before using arctos_update.py for the first time.
It will create the required folder structure, install dependencies,
and move the necessary files into place.

Usage:
    Place setup.py and arctos_update.py anywhere on your computer, then run:
    python3 setup.py
"""

import sys
import subprocess
import shutil
from pathlib import Path

# ============================================================================
# Requirements
# ============================================================================

REQUIRED_PACKAGES = [
    "pandas",
    "tableauhyperapi",
]

MIN_PYTHON = (3, 8)

# ============================================================================
# Steps
# ============================================================================

def check_python_version():
    print("Checking Python version...")
    v = sys.version_info
    if v < MIN_PYTHON:
        print(f"  ❌ Python {v.major}.{v.minor} detected. Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ is required.")
        print("     Download Python at: https://www.python.org/downloads/")
        sys.exit(1)
    print(f"  ✅ Python {v.major}.{v.minor}.{v.micro}")


def install_packages():
    print("\nInstalling required packages...")
    for pkg in REQUIRED_PACKAGES:
        print(f"  Installing {pkg}...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", pkg],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"  ✅ {pkg}")
        else:
            print(f"  ❌ Failed to install {pkg}:")
            print(result.stderr)
            sys.exit(1)


def create_folder_structure():
    print("\nCreating folder structure...")
    script_dir = Path(__file__).parent

    # Create arctos_update/ as the project root if not already inside it
    project_dir = script_dir / "arctos_update"
    if script_dir.name == "arctos_update":
        # Already inside the project folder
        project_dir = script_dir

    dirs = [
        project_dir / "data" / "input",
        project_dir / "data" / "output",
        project_dir / "logs",
    ]

    for d in dirs:
        if not d.exists():
            d.mkdir(parents=True, exist_ok=True)
            print(f"  📁 Created: {d.relative_to(project_dir.parent)}")
        else:
            print(f"  ✅ Already exists: {d.relative_to(project_dir.parent)}")

    # Move setup.py and arctos_update.py into project_dir if not already there
    for filename in ["setup.py", "arctos_update.py"]:
        src = script_dir / filename
        dst = project_dir / filename
        if src != dst and src.exists() and not dst.exists():
            shutil.copy2(src, dst)
            print(f"  📄 Copied {filename} → {project_dir.relative_to(project_dir.parent)}/")

    return project_dir


def print_next_steps(project_dir):
    print()
    print("=" * 60)
    print("✅ Setup complete!")
    print()
    print("Your project folder is ready at:")
    print(f"  {project_dir}")
    print()
    print("Next steps:")
    print()
    print("  1. Copy the following into arctos_update/data/input/ :")
    print("       - Latest Arctos data export  (.csv.gz)")
    print("       - cache_sysstats_global_YYYY-MM-DD.csv")
    print()
    print("  2. Copy the most recent Arctos Tableau .twbx file into arctos_update/ :")
    print("       (same folder as arctos_update.py)")
    print()
    print("  3. Open Terminal, navigate to the folder, and run:")
    print("       cd " + str(project_dir))
    print("       python3 arctos_update.py")
    print()
    print("  4. When done (~8-10 min), close and reopen the .twbx in Tableau")
    print("=" * 60)


# ============================================================================
# Main
# ============================================================================

def main():
    print("=" * 60)
    print("Arctos Dashboard Update Tool — Setup")
    print("=" * 60)
    print()

    check_python_version()
    install_packages()
    project_dir = create_folder_structure()
    print_next_steps(project_dir)


if __name__ == "__main__":
    main()
