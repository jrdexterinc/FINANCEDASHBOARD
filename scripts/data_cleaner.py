#!/usr/bin/env python3
"""
Data Cleaner for Two Years of Giving CSV
Cleans raw donation data and creates:
1. Master donation file (cleaned and standardized)
2. Donor lookup table (unique Donor_ID, First Name, Last Name)
"""

import pandas as pd
import sys
from datetime import datetime
from pathlib import Path

# Configuration
INPUT_FILE = Path(__file__).parent.parent / "data" / "Two_Years_of_Giving_Through_2026.csv"
OUTPUT_MASTER = Path(__file__).parent.parent / "data" / "master_donations_cleaned.csv"
OUTPUT_DONORS = Path(__file__).parent.parent / "data" / "donor_lookup.csv"

# Fields to remove
FIELDS_TO_REMOVE = [
    "dp_RecordName",
    "dp_Selected", 
    "dp_RecordStatus",
    "First Name",
    "Last Name",
    "Campaign Name"
]


def load_data(filepath):
    """Load the raw CSV file"""
    print(f"Loading data from {filepath}...")
    try:
        df = pd.read_csv(filepath, dtype=str)
        print(f"Loaded {len(df)} records")
        return df
    except Exception as e:
        print(f"Error loading file: {e}")
        sys.exit(1)


def clean_donation_date(date_str):
    """Convert donation date to YYYY-MM-DD format"""
    if pd.isna(date_str) or date_str.strip() == "":
        return None
    
    try:
        # Parse various date formats, extract only the date part
        dt = pd.to_datetime(date_str)
        return dt.strftime("%Y-%m-%d")
    except:
        return None


def clean_amount(amount_str):
    """Convert amount to 2 decimal places"""
    if pd.isna(amount_str) or amount_str.strip() == "":
        return None
    
    try:
        amount = float(amount_str)
        return f"{amount:.2f}"
    except:
        return None


def validate_record(row):
    """
    Validate record for missing Donor ID or zero/invalid amounts
    Returns flag status: 'valid', 'missing_donor_id', or 'invalid_amount'
    """
    donor_id = row.get('Donor ID', '').strip()
    amount = row.get('Amount', '').strip()
    
    if not donor_id or donor_id == '':
        return 'missing_donor_id'
    
    try:
        amount_val = float(amount)
        if amount_val <= 0:
            return 'invalid_amount'
    except:
        return 'invalid_amount'
    
    return 'valid'


def clean_data(df):
    """Clean and standardize the data"""
    print("\nCleaning data...")
    
    # Remove specified fields
    df = df.drop(columns=FIELDS_TO_REMOVE, errors='ignore')
    
    # Clean Donation Date - convert to YYYY-MM-DD
    df['Donation Date'] = df['Donation Date'].apply(clean_donation_date)
    
    # Clean Amount - standardize to 2 decimal places
    df['Amount'] = df['Amount'].apply(clean_amount)
    
    # Add validation flag column
    df['data_flag'] = df.apply(validate_record, axis=1)
    
    # Report flagged records
    flag_counts = df['data_flag'].value_counts()
    print(f"Record validation results:")
    print(f"  Valid records: {flag_counts.get('valid', 0)}")
    if 'missing_donor_id' in flag_counts.index:
        print(f"  Missing Donor ID: {flag_counts['missing_donor_id']}")
    if 'invalid_amount' in flag_counts.index:
        print(f"  Invalid Amount: {flag_counts['invalid_amount']}")
    
    return df


def create_master_file(df, output_path):
    """Save cleaned master file"""
    print(f"\nSaving master file to {output_path}...")
    df.to_csv(output_path, index=False)
    print(f"Master file created with {len(df)} records")


def create_donor_lookup(raw_df, output_path):
    """Create unique donor lookup table"""
    print(f"\nCreating donor lookup table...")
    
    # Create lookup with original first/last names
    lookup_df = raw_df[['Donor ID', 'First Name', 'Last Name']].copy()
    
    # Remove duplicates, keeping first occurrence
    lookup_df = lookup_df.drop_duplicates(subset=['Donor ID'], keep='first')
    
    # Remove rows with empty Donor IDs
    lookup_df = lookup_df[lookup_df['Donor ID'].str.strip() != '']
    
    # Sort by Donor ID
    lookup_df = lookup_df.sort_values('Donor ID').reset_index(drop=True)
    
    # Save
    lookup_df.to_csv(output_path, index=False)
    print(f"Donor lookup created with {len(lookup_df)} unique donors")


def main():
    """Main execution"""
    print("=" * 60)
    print("DATA CLEANER - Two Years of Giving Through 2026")
    print("=" * 60)
    
    # Load raw data
    df = load_data(INPUT_FILE)
    
    # Clean data
    cleaned_df = clean_data(df)
    
    # Create master file
    create_master_file(cleaned_df, OUTPUT_MASTER)
    
    # Create donor lookup (use original raw data)
    create_donor_lookup(df, OUTPUT_DONORS)
    
    print("\n" + "=" * 60)
    print("CLEANING COMPLETE!")
    print(f"Master file: {OUTPUT_MASTER}")
    print(f"Donor lookup: {OUTPUT_DONORS}")
    print("=" * 60)


if __name__ == "__main__":
    main()
