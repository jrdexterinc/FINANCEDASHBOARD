#!/usr/bin/env python3
import json
from datetime import datetime
from pathlib import Path
import sys


def load_json(path):
    p = Path(path)
    if not p.exists():
        print(f"FAIL: {path} does not exist")
        sys.exit(1)
    with open(p, 'r') as f:
        return json.load(f)


def is_sunday(iso_ts):
    try:
        dt = datetime.fromisoformat(iso_ts)
    except Exception:
        # try trimming timezone
        dt = datetime.fromisoformat(iso_ts.split('Z')[0])
    return dt.weekday() == 6


def main():
    base = Path(__file__).parent.parent / 'data'
    contrib_file = base / 'contributions_2026.json'
    donors_file = base / 'donors_2026.json'

    contrib = load_json(contrib_file)
    donors = load_json(donors_file)

    # Check reportWeekEnding exists and is a Sunday
    rwe = contrib.get('reportWeekEnding')
    if not rwe:
        print('FAIL: reportWeekEnding not found in contributions_2026.json')
        sys.exit(1)
    if not is_sunday(rwe):
        print(f"FAIL: reportWeekEnding ({rwe}) is not a Sunday")
        sys.exit(1)

    # Basic structure checks
    if 'overview' not in donors:
        print('FAIL: donors_2026.json missing "overview"')
        sys.exit(1)

    # Distinct givers check (basic sanity)
    week = contrib.get('weekly', [])
    if not isinstance(week, list) or len(week) == 0:
        print('WARN: contributions_2026.json weekly data missing or empty (not fatal)')

    print('PASS: smoke tests passed')


if __name__ == '__main__':
    main()
