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
  - Weekly Contributions Trend Chart
  - Giving Method Distribution (Doughnut Chart)
  - Budget vs Actual Comparison (Bar Chart)
  - Year-over-Year Comparison (Bar Chart)

- **Data Tables**
  - Recent Large Gifts Display
  - Budget Category Breakdown

## Project Structure

```
FinanceDashboard/
├── index.html              # Main dashboard HTML
├── scripts/
│   ├── main.js            # Dashboard initialization and KPI updates
│   ├── charts.js          # Chart creation and management
│   └── data-loader.js     # Data loading and calculations
├── styles/
│   └── dashboard.css      # Styling and responsive design
├── data/
│   ├── budget_2026.json   # Budget data
│   ├── contributions_2026.json  # Contribution and giving data
│   └── donors_2026.json   # Donor information
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## Technologies Used

- HTML5
- CSS3
- JavaScript (ES6+)
- Chart.js 4.4.0 for data visualization
- JSON for data storage

## Getting Started

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

## Data Files

- **budget_2026.json**: Contains annual budget and category breakdowns
- **contributions_2026.json**: Contains contribution data, giving methods, and year-over-year comparisons
- **donors_2026.json**: Contains donor information

## Auto-Refresh

The dashboard automatically refreshes every 5 minutes to display the latest data.

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
