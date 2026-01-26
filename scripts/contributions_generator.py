#!/usr/bin/env python3
"""
Contributions Generator for 2026
Creates contributions_2026.json from master donations file
Includes weekly metrics, YoY comparison, and giving analysis
"""

import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Configuration
INPUT_FILE = Path(__file__).parent.parent / "data" / "master_donations_cleaned.csv"
OUTPUT_FILE = Path(__file__).parent.parent / "data" / "contributions_2026.json"

# Budget - you may need to adjust this
WEEKLY_BUDGET = 157128
MONTHLY_BUDGETS = {
    1: 475190, 2: 425000, 3: 512000, 4: 487500, 5: 502000, 6: 495000,
    7: 521000, 8: 538000, 9: 514000, 10: 528000, 11: 612000, 12: 687000
}

# Large gift threshold
LARGE_GIFT_THRESHOLD = 10000

# Donation categories
UNDESIGNATED_CATEGORIES = ['Tithes', 'Offering']
PROCESSING_FEE_CATEGORIES = ['Credit Card Processing Fees']
LEGACY_CATEGORIES = ['Annual Legacy Gift']


def load_data(filepath):
    """Load the master donations file"""
    print(f"Loading data from {filepath}...")
    try:
        df = pd.read_csv(filepath)
        # Filter out flagged invalid records
        df = df[df['data_flag'] == 'valid'].copy()
        df['Donation Date'] = pd.to_datetime(df['Donation Date'])
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
        print(f"Loaded {len(df)} valid records")
        return df
    except Exception as e:
        print(f"Error loading file: {e}")
        sys.exit(1)


def categorize_donation(statement_title):
    """Categorize donation as Undesignated, Processing Fees, Legacy, or Designated"""
    if any(cat in statement_title for cat in PROCESSING_FEE_CATEGORIES):
        return 'Processing Fees'
    elif any(cat in statement_title for cat in UNDESIGNATED_CATEGORIES):
        return 'Undesignated'
    elif any(cat in statement_title for cat in LEGACY_CATEGORIES):
        return 'Legacy'
    else:
        return 'Designated'


def map_payment_method(payment_type):
    """Map payment type to giving method"""
    if payment_type == 'Credit Card':
        return 'Online'
    elif payment_type == 'ACH/EFT':
        return 'ACH'
    elif payment_type == 'Cash':
        return 'Cash'
    elif 'Check' in payment_type:
        return 'Check'
    else:
        return 'Other'


def get_week_of_year(date):
    """Get the Monday-Sunday week number and end date for a given date"""
    # Monday = 0, Sunday = 6
    days_since_monday = date.weekday()  # 0=Monday, 6=Sunday
    
    # Find the Sunday (end of week)
    days_until_sunday = 6 - days_since_monday
    sunday = date + timedelta(days=days_until_sunday)
    
    # Get week number (ISO week)
    return sunday.isocalendar()[1], sunday


def process_year_data(df, year, cutoff_date=None):
    """Process donations for a specific year"""
    year_df = df[df['Donation Date'].dt.year == year].copy()
    
    if cutoff_date:
        year_df = year_df[year_df['Donation Date'] <= cutoff_date]
    
    # Add categorization columns
    year_df['Category'] = year_df['Statement Title'].apply(categorize_donation)
    year_df['Method'] = year_df['Payment Type'].apply(map_payment_method)
    year_df['Week'] = year_df['Donation Date'].apply(lambda x: get_week_of_year(x))
    
    return year_df


def get_weekly_metrics(df, year, week_num):
    """Get metrics for a specific week"""
    week_data = df[
        (df['Donation Date'].dt.year == year) &
        (df['Week'].apply(lambda x: x[0] == week_num))
    ]
    
    if len(week_data) == 0:
        return {
            'amount': 0,
            'givers': 0,
            'by_category': {'Undesignated': 0, 'Legacy': 0, 'Designated': 0},
            'end_date': None
        }
    
    total = week_data['Amount'].sum()
    givers = week_data['Donor ID'].nunique()
    
    by_category = {
        'Undesignated': week_data[week_data['Category'] == 'Undesignated']['Amount'].sum(),
        'Legacy': week_data[week_data['Category'] == 'Legacy']['Amount'].sum(),
        'Designated': week_data[week_data['Category'] == 'Designated']['Amount'].sum()
    }
    
    end_date = week_data['Week'].iloc[0][1]
    
    return {
        'amount': round(total, 2),
        'givers': givers,
        'by_category': {k: round(v, 2) for k, v in by_category.items()},
        'end_date': end_date.strftime('%m/%d')
    }


def build_weekly_trend(df, year, cutoff_date=None):
    """Build weekly trend for the year, only including complete weeks"""
    trend = []
    for week in range(1, 53):
        metrics = get_weekly_metrics(df, year, week)
        if metrics['end_date']:
            # Only include weeks where the end date is before or on the cutoff date
            week_end = datetime.strptime(f"{year}-{metrics['end_date']}", "%Y-%m/%d")
            if cutoff_date and week_end > cutoff_date:
                continue
            trend.append({
                'week': metrics['end_date'],
                'amount': metrics['amount'],
                'year': year
            })
    return trend


def build_rolling_trend(df, current_year, current_cutoff, previous_year, previous_cutoff, weeks=10):
    """Build a rolling N-week trend spanning two years (Nov/Dec + Jan)"""
    all_weeks = []
    
    # Get previous year (2025) weeks - we'll get all of them
    for week in range(1, 53):
        metrics = get_weekly_metrics(df, previous_year, week)
        if metrics['end_date']:
            week_end = datetime.strptime(f"{previous_year}-{metrics['end_date']}", "%Y-%m/%d")
            # Only include weeks from November onward
            if week_end.month >= 11:
                all_weeks.append({
                    'week': metrics['end_date'],
                    'amount': metrics['amount'],
                    'year': previous_year,
                    'date': week_end
                })
    
    # Get current year (2026) weeks up to cutoff
    for week in range(1, 53):
        metrics = get_weekly_metrics(df, current_year, week)
        if metrics['end_date']:
            week_end = datetime.strptime(f"{current_year}-{metrics['end_date']}", "%Y-%m/%d")
            if week_end <= current_cutoff:
                all_weeks.append({
                    'week': metrics['end_date'],
                    'amount': metrics['amount'],
                    'year': current_year,
                    'date': week_end
                })
    
    # Sort by date
    all_weeks.sort(key=lambda x: x['date'])
    
    # Take the last N weeks
    rolling_weeks = all_weeks[-weeks:]
    
    # Remove the temporary date field
    for week in rolling_weeks:
        del week['date']
    
    return rolling_weeks


def get_monthly_metrics(df, year):
    """Get monthly totals for YoY comparison"""
    monthly = {}
    for month in range(1, 13):
        month_data = df[
            (df['Donation Date'].dt.year == year) &
            (df['Donation Date'].dt.month == month)
        ]
        monthly[month] = round(month_data['Amount'].sum(), 2)
    return monthly


def get_large_gifts(df, year, cutoff_date=None):
    """Get gifts above threshold"""
    year_df = df[df['Donation Date'].dt.year == year].copy()
    if cutoff_date:
        year_df = year_df[year_df['Donation Date'] <= cutoff_date]
    
    large = year_df[year_df['Amount'] >= LARGE_GIFT_THRESHOLD].sort_values(
        'Donation Date', ascending=False
    )[['Donation Date', 'Amount', 'Method', 'Statement Title']].copy()
    
    large['Donation Date'] = large['Donation Date'].dt.strftime('%Y-%m-%d')
    
    gifts = []
    for _, row in large.iterrows():
        gifts.append({
            'date': row['Donation Date'],
            'amount': row['Amount'],
            'method': row['Method'],
            'category': row['Statement Title'][:30]  # Truncate long names
        })
    
    return gifts


def calculate_totals(df, year, cutoff_date=None):
    """Calculate YTD totals by category and method"""
    year_df = df[df['Donation Date'].dt.year == year].copy()
    if cutoff_date:
        year_df = year_df[year_df['Donation Date'] <= cutoff_date]
    
    categories = {}
    for cat in ['Undesignated', 'Processing Fees', 'Legacy', 'Designated']:
        cat_df = year_df[year_df['Category'] == cat]
        categories[cat] = round(cat_df['Amount'].sum(), 2)
    
    methods = {}
    for method in ['Online', 'ACH', 'Cash', 'Check', 'Other']:
        method_df = year_df[year_df['Method'] == method]
        methods[method] = round(method_df['Amount'].sum(), 2)
    
    return categories, methods


def main():
    """Main execution"""
    print("=" * 60)
    print("CONTRIBUTIONS GENERATOR - 2026")
    print("=" * 60)
    
    # Configuration
    current_date = datetime(2026, 1, 25)  # January 25, 2026 (Sunday)
    cutoff_date = datetime(2026, 1, 18)   # Through January 18, 2026 (Sunday - complete week)
    previous_year_date = datetime(2025, 1, 18)  # Same week date in 2025
    
    # Load data
    df = load_data(INPUT_FILE)
    
    # Add categorization for all data
    df['Category'] = df['Statement Title'].apply(categorize_donation)
    df['Method'] = df['Payment Type'].apply(map_payment_method)
    df['Week'] = df['Donation Date'].apply(lambda x: get_week_of_year(x))
    
    print(f"\nProcessing data through {cutoff_date.date()}...")
    
    # Current year metrics (2026)
    current_ytd_categories, current_ytd_methods = calculate_totals(df, 2026, cutoff_date)
    current_ytd_total = sum(current_ytd_categories.values())
    
    # Previous year metrics (2025) for same period
    previous_ytd_categories, previous_ytd_methods = calculate_totals(df, 2025, previous_year_date)
    previous_ytd_total = sum(previous_ytd_categories.values())
    
    # Determine week number from cutoff date
    current_week_num = get_week_of_year(cutoff_date)[0]
    previous_week_num = get_week_of_year(previous_year_date)[0]
    
    # Current week (dynamically calculated)
    current_week = get_weekly_metrics(df, 2026, current_week_num)
    previous_week = get_weekly_metrics(df, 2025, previous_week_num)
    
    # Get current week Donor counts
    current_week_df = df[
        (df['Donation Date'].dt.year == 2026) &
        (df['Donation Date'] >= datetime(2026, 1, 12)) &
        (df['Donation Date'] <= datetime(2026, 1, 18))
    ]
    current_givers = current_week_df['Donor ID'].nunique()
    
    previous_week_df = df[
        (df['Donation Date'].dt.year == 2025) &
        (df['Donation Date'] >= datetime(2025, 1, 12)) &
        (df['Donation Date'] <= datetime(2025, 1, 18))
    ]
    previous_givers = previous_week_df['Donor ID'].nunique()
    
    # MTD (Month to date - January)
    current_mtd = df[
        (df['Donation Date'].dt.year == 2026) &
        (df['Donation Date'].dt.month == 1) &
        (df['Donation Date'] <= cutoff_date)
    ]['Amount'].sum()
    
    previous_mtd = df[
        (df['Donation Date'].dt.year == 2025) &
        (df['Donation Date'].dt.month == 1) &
        (df['Donation Date'] <= previous_year_date)
    ]['Amount'].sum()
    
    # Weekly trend for full year
    current_trend = build_rolling_trend(df, 2026, cutoff_date, 2025, previous_year_date, weeks=10)
    
    # Large gifts
    large_gifts = get_large_gifts(df, 2026, cutoff_date)
    
    # YoY monthly comparison
    current_monthly = get_monthly_metrics(df, 2026)
    previous_monthly = get_monthly_metrics(df, 2025)
    
    # Build JSON structure
    contributions = {
        "lastUpdated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "reportWeekEnding": cutoff_date.strftime("%Y-%m-%dT23:59:59"),
        "currentWeek": {
            "wtd": {
                "actual": round(current_week['amount'], 2),
                "budget": WEEKLY_BUDGET,
                "previousYear": round(previous_week['amount'], 2)
            },
            "mtd": {
                "actual": round(current_mtd, 2),
                "budget": MONTHLY_BUDGETS[1],
                "previousYear": round(previous_mtd, 2)
            },
            "ytd": {
                "actual": round(current_ytd_total, 2),
                "budget": sum(MONTHLY_BUDGETS.values()),
                "previousYear": round(previous_ytd_total, 2)
            },
            "distinctGivers": {
                "current": current_givers,
                "previous": previous_givers
            },
            "donationCategories": {
                "Undesignated": current_ytd_categories['Undesignated'],
                "Processing Fees": current_ytd_categories['Processing Fees'],
                "Legacy": current_ytd_categories['Legacy'],
                "Designated": current_ytd_categories['Designated']
            },
            "givingMethods": {
                "Online": current_ytd_methods.get('Online', 0),
                "ACH": current_ytd_methods.get('ACH', 0),
                "Cash": current_ytd_methods.get('Cash', 0),
                "Check": current_ytd_methods.get('Check', 0),
                "Other": current_ytd_methods.get('Other', 0)
            },
            "weeklyTrend": current_trend,
            "yoyComparison": [
                {
                    "month": "Jan",
                    "current": current_monthly.get(1, 0),
                    "previous": previous_monthly.get(1, 0)
                },
                {
                    "month": "Feb",
                    "current": current_monthly.get(2, 0),
                    "previous": previous_monthly.get(2, 0)
                },
                {
                    "month": "Mar",
                    "current": current_monthly.get(3, 0),
                    "previous": previous_monthly.get(3, 0)
                },
                {
                    "month": "Apr",
                    "current": current_monthly.get(4, 0),
                    "previous": previous_monthly.get(4, 0)
                },
                {
                    "month": "May",
                    "current": current_monthly.get(5, 0),
                    "previous": previous_monthly.get(5, 0)
                },
                {
                    "month": "Jun",
                    "current": current_monthly.get(6, 0),
                    "previous": previous_monthly.get(6, 0)
                },
                {
                    "month": "Jul",
                    "current": current_monthly.get(7, 0),
                    "previous": previous_monthly.get(7, 0)
                },
                {
                    "month": "Aug",
                    "current": current_monthly.get(8, 0),
                    "previous": previous_monthly.get(8, 0)
                },
                {
                    "month": "Sep",
                    "current": current_monthly.get(9, 0),
                    "previous": previous_monthly.get(9, 0)
                },
                {
                    "month": "Oct",
                    "current": current_monthly.get(10, 0),
                    "previous": previous_monthly.get(10, 0)
                },
                {
                    "month": "Nov",
                    "current": current_monthly.get(11, 0),
                    "previous": previous_monthly.get(11, 0)
                },
                {
                    "month": "Dec",
                    "current": current_monthly.get(12, 0),
                    "previous": previous_monthly.get(12, 0)
                }
            ]
        }
    }
    
    # Save to file
    print(f"\nSaving contributions file to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(contributions, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Period: Through Sunday, January 18, 2026")
    print(f"\nWeek (Jan 12-18):")
    print(f"  Current: ${current_week['amount']:,.2f}")
    print(f"  Previous Year: ${previous_week['amount']:,.2f}")
    print(f"\nMonth to Date (January):")
    print(f"  Current: ${current_mtd:,.2f}")
    print(f"  Previous Year: ${previous_mtd:,.2f}")
    print(f"\nYear to Date:")
    print(f"  Current: ${current_ytd_total:,.2f}")
    print(f"  Previous Year: ${previous_ytd_total:,.2f}")
    print(f"\nDistinct Givers (Week):")
    print(f"  Current: {current_givers}")
    print(f"  Previous Year: {previous_givers}")
    print(f"\nLarge Gifts (>${LARGE_GIFT_THRESHOLD:,.0f}): {len(large_gifts)}")
    print(f"\nFile saved: {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
