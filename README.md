# Impact Church Financial Dashboard

This is an **Impact Church Financial Dashboard** created with assistance from AI. **No company data or personal data was compromised.**

## Overview

A comprehensive financial dashboard for Impact Church that provides real-time insights into giving patterns, budget tracking, and financial metrics. The dashboard displays key performance indicators, visualizations of contribution trends, and detailed financial data.

## Features

- **Key Performance Indicators (KPIs)**
  - Week-to-Date (WTD) Contributions
  - Month-to-Date (MTD) Contributions
  - Year-to-Date (YTD) Contributions
  - Distinct Givers Count

- **Visual Analytics**
  - Weekly Contributions Trend Chart (rolling 10-week view)
  - Giving Method Distribution (Doughnut Chart - Online, ACH, Cash, Check, Other)
  - Contributions by Category (Doughnut Chart - Undesignated, Processing Fees, Legacy, Designated)
  - Budget vs Actual Comparison (Bar Chart)
  - Year-over-Year Comparison (Bar Chart)

- **Data Tables**
  - Recent Large Gifts Display ($10,000+)
  - Budget Category Breakdown

- **Data Processing**
  - Automated CSV data cleaning and validation
  - Master donations file generation
  - Donor lookup table creation
  - Weekly JSON report generation

## Project Structure

```
FinanceDashboard/
├── index.html                          # Main dashboard HTML
├── README.md                           # This file
├── scripts/
│   ├── run_all.py                      # Master script to run all data generation scripts
│   ├── main.js                         # Dashboard initialization and KPI updates
│   ├── charts.js                       # Chart creation and management
│   ├── data-loader.js                  # Data loading and calculations
│   ├── data_cleaner.py                 # Raw CSV cleaning and validation
│   ├── contributions_generator.py      # Weekly JSON report generation
│   └── donor_insights_generator.py     # Donor insights and segmentation
├── styles/
│   └── dashboard.css                   # Styling and responsive design
├── data/
│   ├── Two_Years_of_Giving_Through_2026.csv  # Raw donation data
│   ├── master_donations_cleaned.csv           # Cleaned donation data
│   ├── donor_lookup.csv                       # Unique donor reference table
│   ├── budget_2026.json                       # Budget data
│   ├── contributions_2026.json                # Weekly contribution report
│   └── donors_2026.json                       # Donor information and segments
└── .gitignore                          # Git ignore rules
```

## Technologies Used

- HTML5
- CSS3
- JavaScript (ES6+)
- Python 3 (data processing)
- Chart.js 4.4.0 for data visualization
- Pandas (data manipulation)
- JSON for data storage

## Getting Started

### Dashboard Setup

1. Clone the repository:

```bash
git clone https://github.com/jrdexterinc/FINANCEDASHBOARD.git
```

2. Navigate to the project directory:

```bash
cd FINANCEDASHBOARD
```

3. Open `index.html` in a modern web browser or serve it locally:

```bash
# Using Python
python -m http.server 8000

# Using Node.js http-server
npx http-server
```

4. Visit `http://localhost:8000` in your browser

### Weekly Data Processing Workflow

1. **Export raw donation data** from your giving system as `Two_Years_of_Giving_Through_2026.csv` and place in the `data/` directory

2. **Run all data processing scripts** (recommended):

```bash
# Run all scripts at once
python3 scripts/run_all.py

# Or run individual scripts
python3 scripts/run_all.py cleaner          # Clean and validate data
python3 scripts/run_all.py contributions    # Generate weekly report
python3 scripts/run_all.py insights         # Generate donor insights

# View available scripts
python3 scripts/run_all.py --list
```

**What each script does:**

- **data_cleaner.py** - Cleans raw CSV data and generates:
  - `master_donations_cleaned.csv` - Cleaned, standardized donation records
  - `donor_lookup.csv` - Unique donor reference table

- **contributions_generator.py** - Generates weekly contribution report:
  - `contributions_2026.json` - Weekly metrics and analytics for the dashboard

- **donor_insights_generator.py** - Generates donor insights:
  - `donors_2026.json` - Donor information and segments

3. **Refresh the dashboard** - The dashboard will automatically load the updated JSON data

## Data Files

### Input Files

- **Two_Years_of_Giving_Through_2026.csv**: Raw donation export from giving system

### Generated Files

- **master_donations_cleaned.csv**: Cleaned donation records with:
  - Standardized dates (YYYY-MM-DD format)
  - Standardized amounts (2 decimal places)
  - Validation flags for data quality
  - Removed sensitive fields

- **donor_lookup.csv**: Unique donor reference table with Donor ID, First Name, and Last Name for lookups

- **contributions_2026.json**: Weekly dashboard report containing:
  - Week-to-Date, Month-to-Date, Year-to-Date metrics
  - Budget comparisons
  - Distinct giver counts
  - Donations by category (Undesignated, Processing Fees, Legacy, Designated)
  - Giving methods breakdown (Online, ACH, Cash, Check, Other)
  - Rolling 10-week trend (Nov 2025 - current)
  - Year-over-year monthly comparisons
  - Large gifts ($10,000+)

### Reference Files

- **budget_2026.json**: Annual budget allocations
- **donors_2026.json**: Donor information

## Data Processing Details

### Master Script (`run_all.py`)

Convenient command-line tool to run all data generation scripts:

```bash
# Run all scripts in order (cleaner → contributions → insights)
python3 scripts/run_all.py

# Run a specific script
python3 scripts/run_all.py cleaner
python3 scripts/run_all.py contributions
python3 scripts/run_all.py insights

# List available scripts
python3 scripts/run_all.py --list
```

Features:

- Run all scripts in the correct dependency order
- Run individual scripts as needed
- Clear progress output with status indicators
- Error handling and summary reporting

### Data Cleaner (`data_cleaner.py`)

Cleans raw CSV donation data with the following features:

- Removes sensitive fields: dp_RecordName, dp_Selected, dp_RecordStatus, First Name, Last Name, Campaign Name
- Standardizes donation dates to YYYY-MM-DD format
- Formats amounts to 2 decimal places
- Validates records and flags entries with:
  - Missing Donor ID
  - Invalid/zero amounts
- Generates master file suitable for weekly analytics
- Creates donor lookup table for reference

### Contributions Generator (`contributions_generator.py`)

Generates weekly analytics report with:

- **Donation Categories**:
  - Undesignated (Tithes, Offerings)
  - Processing Fees (Credit Card Processing Fees)
  - Legacy (Annual Legacy Gifts)
  - Designated (All other categories)

- **Payment Methods**:
  - Online (Credit Card)
  - ACH (ACH/EFT)
  - Cash
  - Check
  - Other

- **Time Periods**:
  - Week-to-Date (Monday-Sunday)
  - Month-to-Date
  - Year-to-Date
  - Year-over-Year comparisons (2025 vs 2026)

- **Visualizations**:
  - Rolling 10-week trend (November 2025 through current week)
  - Monthly comparisons (Jan-Dec)
  - Large gifts over $10,000

### Budget Data

Weekly budget: $157,128
Monthly budgets configured for all 12 months

## Dashboard Features

### Auto-Refresh

The dashboard automatically refreshes every 5 minutes to display the latest data.

### Chart Visualizations

- **Weekly Contributions Trend**: Line chart showing rolling 10-week trend spanning November 2025 through current week
- **Giving Method Distribution**: Doughnut chart showing contributions by payment method (Online, ACH, Cash, Check, Other)
- **Contributions by Category**: Doughnut chart showing donations by category type (Undesignated, Processing Fees, Legacy, Designated)
- **Budget vs Actual**: Bar chart comparing budgeted vs actual giving by category
- **Year-over-Year Comparison**: Monthly comparison between current year and previous year

## Browser Compatibility

- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge

## Notes

- All data displayed is sample/test data
- The dashboard uses responsive design and adapts to different screen sizes
- Chart.js is loaded via CDN for visualization

## License

Internal use only

---

_Created with AI assistance to enhance financial transparency and decision-making at Impact Church._

### Budget input: `data/budget_2026.json`

Place a `budget_2026.json` file in the `data/` folder when ready. The scripts currently read budget values from the constants in `scripts/contributions_generator.py`. If you'd like the scripts to load budgets from `budget_2026.json` automatically, I can update the generator to do that.

Expected minimal structure (example):

```json
{
  "year": 2026,
  "weekly_budget": 157128,
  "monthly_budgets": {
    "1": 475190,
    "2": 425000,
    "3": 512000,
    "4": 487500,
    "5": 502000,
    "6": 495000,
    "7": 521000,
    "8": 538000,
    "9": 514000,
    "10": 528000,
    "11": 612000,
    "12": 687000
  }
}
```

Notes:

- File path: `data/budget_2026.json`
- Keys: `year` (number), `weekly_budget` (number), `monthly_budgets` (object mapping month number to amount).
- If you want me to make the scripts automatically read this file, tell me and I'll implement it.
