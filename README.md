# Evaluating a Manufacturing Process with SQL

Statistical Process Control (SPC) analysis of a manufacturing process using SQL window functions, Python, and an interactive Streamlit dashboard.

---

## Overview

Manufacturing quality control relies on monitoring whether measurements stay within acceptable bounds. This project implements **SPC** on historical height measurements from a manufacturing line, using a rolling window of 5 observations per operator to compute dynamic control limits.

Control limits are defined as:

```
UCL = avg_height + (3 × stddev_height / √5)
LCL = avg_height − (3 × stddev_height / √5)
```

Any measurement outside these limits triggers an alert.

---

## Project Structure

```
├── data/
│   └── raw/
│       └── parts.csv           # Source data (item_no, length, width, height, operator)
├── notebooks/
│   └── analysis.ipynb          # End-to-end analysis: ETL → SPC query → charts → summary
├── sql/
│   ├── window_functions.sql    # Core SPC query using SQL window functions
│   └── analysis_queries.sql    # Exploratory global-stats query (reference)
├── dashboard.py                # Interactive Streamlit dashboard
├── requirements.txt
└── README.md
```

---

## Tech Stack

- **Database:** PostgreSQL
- **Language:** Python 3
- **Libraries:** pandas, SQLAlchemy, psycopg2, matplotlib, Streamlit, Plotly
- **Notebook:** Jupyter

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start PostgreSQL

Make sure a local PostgreSQL instance is running on `localhost:5432` with:
- Database: `postgres`
- User: `postgres`
- Password: `postgres`

Adjust the connection string in `notebooks/analysis.ipynb` and `dashboard.py` if your setup differs.

### 3. Load data & run analysis

Open and run `notebooks/analysis.ipynb` top to bottom. It will:
1. Load `data/raw/parts.csv` into the `manufacturing_parts` table
2. Execute the SPC query and build the `alerts` DataFrame
3. Render control charts (one per operator)
4. Display a per-operator summary table

### 4. Launch the dashboard

```bash
streamlit run dashboard.py
```

The dashboard provides:
- Operator filter
- KPI metrics (total measurements, in/out of control, yield %)
- Interactive control charts with hover and zoom
- Summary table
- Raw data table with an out-of-control filter toggle

---

## The `alerts` DataFrame

The final output has one row per measurement (incomplete windows of < 5 excluded):

| Column | Description |
|---|---|
| `operator` | Machine operator ID |
| `row_number` | Measurement sequence within the operator |
| `height` | Observed height |
| `avg_height` | Rolling 5-row average |
| `stddev_height` | Rolling 5-row standard deviation |
| `ucl` | Upper Control Limit |
| `lcl` | Lower Control Limit |
| `alert` | `TRUE` if outside control limits |
