#!/usr/bin/env python3
"""
Donor Insights Generator for 2026
Creates donors_2026.json with useful donor statistics and segments
"""

import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Configuration
INPUT_FILE = Path(__file__).parent.parent / "data" / "master_donations_cleaned.csv"
OUTPUT_FILE = Path(__file__).parent.parent / "data" / "donors_2026.json"
DONOR_LOOKUP = Path(__file__).parent.parent / "data" / "donor_lookup.csv"

def load_data(filepath):
    """Load the master donations file"""
    print(f"Loading data from {filepath}...")
    try:
        df = pd.read_csv(filepath)
        df['Donation Date'] = pd.to_datetime(df['Donation Date'])
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
        df = df[df['Amount'] > 0]  # Filter out negative amounts
        print(f"Loaded {len(df)} records")
        return df
    except Exception as e:
        print(f"Error loading file: {e}")
        sys.exit(1)


def consolidate_daily_donations(df):
    """Consolidate multiple donations per donor per day into single donation"""
    # Group by Donor ID and Donation Date, summing amounts
    daily_df = df.groupby(['Donor ID', 'Donation Date']).agg({
        'Amount': 'sum',
        'Payment Type': 'first',  # Take first payment method
        'Statement Title': lambda x: list(x.unique())  # Keep all titles given that day
    }).reset_index()
    
    daily_df.rename(columns={'Amount': 'Daily_Total'}, inplace=True)
    return daily_df


def categorize_donation(statement_title):
    """Categorize donation"""
    if 'Credit Card Processing Fees' in statement_title:
        return 'Processing Fees'
    elif any(cat in statement_title for cat in ['Tithes', 'Offering']):
        return 'Undesignated'
    elif 'Annual Legacy Gift' in statement_title:
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


def get_most_recent_sunday(df):
    """Find the most recent complete Sunday in the data"""
    max_date = df['Donation Date'].max()
    days_since_sunday = (max_date.weekday() + 1) % 7
    most_recent_sunday = max_date - timedelta(days=days_since_sunday)
    return most_recent_sunday
def calculate_donor_metrics(df, daily_df, cutoff_year=2026, cutoff_date=None):
    """Calculate key metrics for each donor across multiple time periods"""
    donor_metrics = {}
    
    # Add categorization columns
    df = df.copy()
    df['Category'] = df['Statement Title'].apply(categorize_donation)
    df['Method'] = df['Payment Type'].apply(map_payment_method)
    
    # Default cutoff date to today if not provided
    if cutoff_date is None:
        cutoff_date = df['Donation Date'].max()
    
    # Calculate trailing 12-month start date
    trailing_12_start = cutoff_date - timedelta(days=365)
    
    # Get unique donors
    donors = df['Donor ID'].unique()
    
    for donor_id in donors:
        donor_df = df[df['Donor ID'] == donor_id].copy()
        donor_daily = daily_df[daily_df['Donor ID'] == donor_id].copy()
        
        # Current year (2026) data
        donor_2026 = donor_df[donor_df['Donation Date'].dt.year == cutoff_year]
        donor_daily_2026 = donor_daily[donor_daily['Donation Date'].dt.year == cutoff_year]
        
        # Current month data
        current_month_start = cutoff_date.replace(day=1)
        donor_mtd = donor_2026[donor_2026['Donation Date'] >= current_month_start]
        donor_mtd_daily = donor_daily_2026[donor_daily_2026['Donation Date'] >= current_month_start]
        
        # Previous year (2025) data
        donor_2025 = donor_df[donor_df['Donation Date'].dt.year == cutoff_year - 1]
        
        # Trailing 12-month data
        donor_trailing_12 = donor_df[donor_df['Donation Date'] >= trailing_12_start]
        donor_trailing_12_daily = donor_daily[donor_daily['Donation Date'] >= trailing_12_start]
        
        # Calculate metrics
        metrics = {
            'donor_id': int(donor_id),
            # YTD 2026 metrics
            'ytd_2026': {
                'total': round(donor_2026['Amount'].sum(), 2),
                'gifts': len(donor_daily_2026),
                'giving_days': int(donor_daily_2026['Donation Date'].nunique()),
                'average_gift': round(donor_daily_2026['Daily_Total'].mean(), 2) if len(donor_daily_2026) > 0 else 0,
                'largest_gift': round(donor_daily_2026['Daily_Total'].max(), 2) if len(donor_daily_2026) > 0 else 0,
            },
            # MTD 2026 metrics
            'mtd_2026': {
                'total': round(donor_mtd['Amount'].sum(), 2),
                'gifts': len(donor_mtd_daily),
                'giving_days': int(donor_mtd_daily['Donation Date'].nunique()),
            },
            # YTD 2025 metrics (full year for comparison)
            'ytd_2025': {
                'total': round(donor_2025['Amount'].sum(), 2),
                'gifts': len(donor_daily[donor_daily['Donation Date'].dt.year == 2025]),
            },
            # Trailing 12-month metrics (overall health)
            'trailing_12_month': {
                'total': round(donor_trailing_12['Amount'].sum(), 2),
                'gifts': len(donor_trailing_12_daily),
                'giving_days': int(donor_trailing_12_daily['Donation Date'].nunique()),
                'average_gift': round(donor_trailing_12_daily['Daily_Total'].mean(), 2) if len(donor_trailing_12_daily) > 0 else 0,
            },
            # Lifetime metrics
            'lifetime': {
                'total': round(donor_df['Amount'].sum(), 2),
                'gifts': len(donor_daily),
                'first_gift_date': donor_df['Donation Date'].min().strftime('%Y-%m-%d'),
            },
            # Current activity
            'preferred_method': donor_2026['Method'].mode().values[0] if len(donor_2026) > 0 else 'Unknown',
            'last_gift_date': donor_2026['Donation Date'].max().strftime('%Y-%m-%d') if len(donor_2026) > 0 else None,
            'categories': list(donor_2026['Category'].unique()) if len(donor_2026) > 0 else [],
            # Growth analysis
            'growth_percent': None,
            'is_major_donor': False,
            'is_consistent_giver': False,
        }
        
        # Calculate growth percentage (2026 YTD vs 2025 same period)
        if metrics['ytd_2025']['total'] > 0:
            growth = ((metrics['ytd_2026']['total'] - metrics['ytd_2025']['total']) / metrics['ytd_2025']['total']) * 100
            metrics['growth_percent'] = round(growth, 1)
        
        # Classification flags
        metrics['is_major_donor'] = bool(metrics['ytd_2026']['total'] >= 5000)
        metrics['is_consistent_giver'] = bool(metrics['ytd_2026']['giving_days'] >= 4)
        
        donor_metrics[str(int(donor_id))] = metrics
    
    return donor_metrics


def get_donor_segments(donor_metrics, df, cutoff_date):
    """Classify donors into segments"""
    segments = {
        'major_donors': [],
        'consistent_givers': [],
        'new_donors': [],
        'lapsed_engaged': [],  # Gave 4+ times or $200+ in 2025
        'lapsed_casual': [],   # Gave less than 4 times and under $200 in 2025
        'at_risk_donors': []
    }
    
    today = datetime.now()
    
    # Pre-calculate same period totals for all donors
    same_period_start = cutoff_date.replace(month=1, day=1)
    
    same_period_2025 = df[(df['Donation Date'].dt.year == 2025) & 
                          (df['Donation Date'] >= same_period_start.replace(year=2025))].groupby('Donor ID')['Amount'].sum()
    same_period_2026 = df[(df['Donation Date'].dt.year == 2026) & 
                          (df['Donation Date'] >= same_period_start)].groupby('Donor ID')['Amount'].sum()
    
    for donor_id, metrics in donor_metrics.items():
        donor_id_int = int(donor_id)
        
        # Major donors: $5000+ YTD
        if metrics['is_major_donor']:
            segments['major_donors'].append(donor_id)
        
        # Consistent givers: 4+ giving occasions in current year
        if metrics['is_consistent_giver']:
            segments['consistent_givers'].append(donor_id)
        
        # New donors: First gift in current year
        if metrics['lifetime']['first_gift_date'] and int(metrics['lifetime']['first_gift_date'][:4]) == today.year:
            segments['new_donors'].append(donor_id)
        
        # Lapsed donors: No gifts in current year but gave in 2025
        if metrics['ytd_2026']['total'] == 0 and metrics['ytd_2025']['total'] > 0:
            # Distinguish by engagement level in 2025
            if metrics['ytd_2025']['gifts'] >= 4 or metrics['ytd_2025']['total'] >= 200:
                segments['lapsed_engaged'].append(donor_id)
            else:
                segments['lapsed_casual'].append(donor_id)
        
        # At-risk donors: 50%+ decline comparing same period (Jan 1 - cutoff date)
        total_2025_same = same_period_2025.get(donor_id_int, 0)
        total_2026_same = same_period_2026.get(donor_id_int, 0)
        
        if total_2025_same > 0 and total_2026_same > 0:
            decline = ((total_2026_same - total_2025_same) / total_2025_same) * 100
            if decline < -50:
                segments['at_risk_donors'].append(donor_id)
    
    return segments


def get_overview_stats(donor_metrics, daily_df):
    """Get high-level donor statistics"""
    all_ytd_2026 = [m['ytd_2026']['total'] for m in donor_metrics.values()]
    all_trailing_12 = [m['trailing_12_month']['total'] for m in donor_metrics.values()]
    
    stats = {
        'total_donors': len(donor_metrics),
        'active_donors_2026': len([m for m in donor_metrics.values() if m['ytd_2026']['total'] > 0]),
        'ytd_2026': {
            'average_donor': round(sum(all_ytd_2026) / len(all_ytd_2026) if all_ytd_2026 else 0, 2),
            'median_donor': round(sorted(all_ytd_2026)[len(all_ytd_2026)//2] if all_ytd_2026 else 0, 2),
            'top_donor': max(all_ytd_2026) if all_ytd_2026 else 0,
            'total_gifts': len(daily_df[daily_df['Donation Date'].dt.year == 2026]),
        },
        'trailing_12_month': {
            'average_donor': round(sum(all_trailing_12) / len(all_trailing_12) if all_trailing_12 else 0, 2),
            'total_gifts': len(daily_df[daily_df['Donation Date'] >= (daily_df['Donation Date'].max() - timedelta(days=365))]),
        },
        'average_gift_size_2026': round(daily_df[daily_df['Donation Date'].dt.year == 2026]['Daily_Total'].mean(), 2),
        'growth_donors': len([m for m in donor_metrics.values() if m['growth_percent'] and m['growth_percent'] > 0]),
        'declining_donors': len([m for m in donor_metrics.values() if m['growth_percent'] and m['growth_percent'] < 0])
    }
    
    return stats


def get_monthly_metrics(df, daily_df):
    """Calculate monthly new donors and average gift size by month for 2025 vs 2026"""
    monthly_data = {}
    
    # Get all months from data
    min_date = df['Donation Date'].min()
    max_date = df['Donation Date'].max()
    
    # For each month, track new donors and avg gift
    current_date = min_date.replace(day=1)
    while current_date <= max_date:
        year = current_date.year
        month = current_date.month
        month_key = f"{year}-{month:02d}"
        
        # Get first day of month and first day of next month
        month_start = current_date
        if month == 12:
            month_end = month_start.replace(year=year+1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = month_start.replace(month=month+1, day=1) - timedelta(days=1)
        
        # Find new donors in this month (first gift ever in this month)
        month_daily = daily_df[(daily_df['Donation Date'] >= month_start) & 
                               (daily_df['Donation Date'] <= month_end)]
        
        new_donors = 0
        for donor_id in month_daily['Donor ID'].unique():
            donor_first_gift = df[df['Donor ID'] == donor_id]['Donation Date'].min()
            if donor_first_gift >= month_start and donor_first_gift <= month_end:
                new_donors += 1
        
        # Average gift size for the month
        avg_gift = round(month_daily['Daily_Total'].mean(), 2) if len(month_daily) > 0 else 0
        
        monthly_data[month_key] = {
            'new_donors': new_donors,
            'average_gift': avg_gift,
            'total_gifts': len(month_daily),
            'total_amount': round(month_daily['Daily_Total'].sum(), 2)
        }
        
        # Move to next month
        if month == 12:
            current_date = current_date.replace(year=year+1, month=1)
        else:
            current_date = current_date.replace(month=month+1)
    
    return monthly_data


def main():
    """Main execution"""
    print("=" * 60)
    print("DONOR INSIGHTS GENERATOR - 2026")
    print("=" * 60)
    
    # Load data
    df = load_data(INPUT_FILE)
    
    # Consolidate daily donations
    print("\nConsolidating daily donations...")
    daily_df = consolidate_daily_donations(df)
    
    # Calculate donor metrics
    print("Calculating donor metrics...")
    cutoff_date = get_most_recent_sunday(df)
    donor_metrics = calculate_donor_metrics(df, daily_df, cutoff_year=2026, cutoff_date=cutoff_date)
    
    # Get segments
    print("Classifying donor segments...")
    segments = get_donor_segments(donor_metrics, df, cutoff_date)
    
    # Get overview stats
    overview = get_overview_stats(donor_metrics, daily_df)
    
    # Get monthly metrics
    print("Calculating monthly metrics...")
    monthly_metrics = get_monthly_metrics(df, daily_df)
    
    # Build JSON structure
    donors_report = {
        "lastUpdated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "overview": overview,
        "segments": {
            "major_donors": {
                "count": len(segments['major_donors']),
                "donor_ids": segments['major_donors']
            },
            "consistent_givers": {
                "count": len(segments['consistent_givers']),
                "donor_ids": segments['consistent_givers']
            },
            "new_donors": {
                "count": len(segments['new_donors']),
                "donor_ids": segments['new_donors']
            },
            "lapsed_engaged": {
                "count": len(segments['lapsed_engaged']),
                "donor_ids": segments['lapsed_engaged']
            },
            "lapsed_casual": {
                "count": len(segments['lapsed_casual']),
                "donor_ids": segments['lapsed_casual']
            },
            "at_risk_donors": {
                "count": len(segments['at_risk_donors']),
                "donor_ids": segments['at_risk_donors']
            }
        },
        "monthly_metrics": monthly_metrics,
        "donors": donor_metrics
    }
    
    # Save to file
    print(f"\nSaving donor insights to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(donors_report, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total Donors Analyzed: {overview['total_donors']}")
    print(f"Active Donors (2026): {overview['active_donors_2026']}")
    print(f"\nYTD 2026 Metrics:")
    print(f"  Average Donor: ${overview['ytd_2026']['average_donor']:,.2f}")
    print(f"  Median Donor: ${overview['ytd_2026']['median_donor']:,.2f}")
    print(f"  Top Donor: ${overview['ytd_2026']['top_donor']:,.2f}")
    print(f"  Total Gifts: {overview['ytd_2026']['total_gifts']}")
    print(f"\nTrailing 12-Month Metrics:")
    print(f"  Average Donor: ${overview['trailing_12_month']['average_donor']:,.2f}")
    print(f"  Total Gifts: {overview['trailing_12_month']['total_gifts']}")
    print(f"\nGift Metrics:")
    print(f"  Average Gift Size (2026): ${overview['average_gift_size_2026']:,.2f}")
    print(f"\nDonor Segments:")
    print(f"  Major Donors ($5000+): {len(segments['major_donors'])}")
    print(f"  Consistent Givers (4+ times): {len(segments['consistent_givers'])}")
    print(f"  New Donors: {len(segments['new_donors'])}")
    print(f"  Lapsed Engaged (4+ gifts or $200+ in 2025): {len(segments['lapsed_engaged'])}")
    print(f"  Lapsed Casual (less than 4 gifts and under $200): {len(segments['lapsed_casual'])}")
    print(f"  At-Risk Donors (50%+ decline same period): {len(segments['at_risk_donors'])}")
    print(f"\nGrowth Analysis:")
    print(f"  Growing Donors: {overview['growth_donors']}")
    print(f"  Declining Donors: {overview['declining_donors']}")
    print(f"\nFile saved: {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
