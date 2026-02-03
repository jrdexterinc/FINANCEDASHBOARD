#!/usr/bin/env python3
"""
Master script to run all data generation scripts
Allows running all scripts at once or individually
"""

import subprocess
import sys
import argparse
from pathlib import Path

# Get the scripts directory
SCRIPTS_DIR = Path(__file__).parent

# Define available scripts with descriptions
SCRIPTS = {
    "cleaner": {
        "name": "data_cleaner.py",
        "description": "Clean raw donation data and create master file",
    },
    "contributions": {
        "name": "contributions_generator.py",
        "description": "Generate weekly contributions data",
    },
    "insights": {
        "name": "donor_insights_generator.py",
        "description": "Generate donor insights and segments",
    },
}

SCRIPT_ORDER = ["cleaner", "contributions", "insights"]


def run_script(script_key):
    """Run a single script"""
    script_info = SCRIPTS[script_key]
    script_path = SCRIPTS_DIR / script_info["name"]

    if not script_path.exists():
        print(f"❌ Error: {script_info['name']} not found")
        return False

    print(f"\n{'='*60}")
    print(f"Running: {script_info['description']}")
    print(f"File: {script_info['name']}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            check=True,
        )
        print(f"✅ {script_info['name']} completed successfully\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {script_info['name']} failed with exit code {e.returncode}\n")
        return False
    except Exception as e:
        print(f"❌ Error running {script_info['name']}: {e}\n")
        return False


def run_all_scripts():
    """Run all scripts in the correct order"""
    print("\n🚀 Starting all data generation scripts...")
    results = {}

    for script_key in SCRIPT_ORDER:
        results[script_key] = run_script(script_key)

    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print(f"{'='*60}")
    for script_key in SCRIPT_ORDER:
        status = "✅ PASSED" if results[script_key] else "❌ FAILED"
        print(f"{status} - {SCRIPTS[script_key]['name']}")

    all_passed = all(results.values())
    print(f"{'='*60}\n")

    return 0 if all_passed else 1


def print_script_list():
    """Print available scripts"""
    print("\nAvailable scripts:")
    print("-" * 60)
    for key in SCRIPT_ORDER:
        print(f"  {key:15} - {SCRIPTS[key]['description']}")
    print("-" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Run data generation scripts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_all.py              # Run all scripts
  python run_all.py cleaner      # Run only data cleaner
  python run_all.py contributions # Run only contributions generator
  python run_all.py insights     # Run only donor insights generator
  python run_all.py --list       # List available scripts
        """,
    )

    parser.add_argument(
        "script",
        nargs="?",
        help="Script to run (cleaner, contributions, insights)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available scripts",
    )

    args = parser.parse_args()

    if args.list:
        print_script_list()
        return 0

    if args.script:
        if args.script not in SCRIPTS:
            print(f"❌ Unknown script: {args.script}")
            print_script_list()
            return 1
        return 0 if run_script(args.script) else 1
    else:
        return run_all_scripts()


if __name__ == "__main__":
    sys.exit(main())
