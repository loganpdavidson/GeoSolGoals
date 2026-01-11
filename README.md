# GeoSolGoals 📊

An interactive dashboard for tracking progress toward yearly financial goals and monitoring accounts receivable for Geographic Solutions.

## Features

- **Year-to-Date Goal Progress**: Track total payments received and progress toward your yearly goal (default: $80,000)
- **Accounts Receivable Status**: Monitor outstanding invoices and amounts
- **Monthly Breakdown**: Visualize payments by month with target comparisons
- **Dynamic Configuration**: Customize your yearly goal and filter by year
- **Excel/CSV Support**: Upload your data files or use the included sample data

## Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/loganpdavidson/GeoSolGoals.git
cd GeoSolGoals
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Dashboard

Start the Streamlit dashboard:
```bash
streamlit run app.py
```

The dashboard will open in your default web browser at `http://localhost:8501`.

### Using Your Data

1. **Upload your file**: Use the file uploader in the sidebar to upload your Excel (.xlsx, .xls) or CSV file
2. **Or use sample data**: Check the "Use sample data" option to explore the dashboard with example data

### Data Format

Your data file should include the following columns:

| Column | Description |
|--------|-------------|
| Client | Client name |
| Type | Type of engagement (Contract, Project, etc.) |
| Year | Year of the invoice |
| Quarter | Quarter (Q1, Q2, Q3, Q4) |
| Amount | Invoice amount (numeric) |
| Sent | Whether invoice was sent (Yes/No) |
| Date Sent | Date the invoice was sent |
| Payment Received | Whether payment was received (Yes/No) |
| Payment Received Date | Date the payment was received |

### Customizing the Goal

Use the "Yearly Goal ($)" input in the sidebar to set your target revenue goal. The default is $80,000.

## Sample Data

A sample dataset (`sample_data.csv`) is included in the repository for testing and demonstration purposes.

## Dashboard Views

- **Overview Metrics**: Quick view of payments received, outstanding AR, and goal progress
- **Progress Gauge**: Visual representation of progress toward your goal
- **Monthly Breakdown**: Bar chart comparing actual payments vs monthly targets
- **Outstanding AR**: Detailed view of unpaid invoices by client
- **Data Export**: Download filtered data as CSV

## Technologies Used

- **Streamlit**: Interactive web application framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualizations and charts
- **OpenPyXL**: Excel file handling

## License

This project is licensed under the MIT License.

## Support

For issues or questions, please open an issue on GitHub.
