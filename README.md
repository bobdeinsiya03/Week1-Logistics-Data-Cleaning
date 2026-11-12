# Week 1: Data Collection and Cleaning Strategies in Logistics

This repository contains Python code for exploring, cleaning, integrating, and analyzing the Olist Brazilian E-Commerce Public Dataset.

## Project tasks
- Load orders, order items, and customers data.
- Inspect data types, missing values, and duplicate records.
- Convert order timestamps to datetime.
- Clean text fields and remove duplicate rows.
- Merge the datasets using `customer_id` and `order_id`.
- Classify delivery performance as On Time, Late, or Unknown / Not Delivered.
- Calculate delivery duration.
- Generate charts and export cleaned datasets.

## Dataset setup
Download the Olist Brazilian E-Commerce Public Dataset from Kaggle. Place these three CSV files in a folder named `data`:

- `olist_orders_dataset.csv`
- `olist_order_items_dataset.csv`
- `olist_customers_dataset.csv`

Your folder structure should look like this:

```text
Week1_Logistics_GitHub/
├── data/
│   ├── olist_orders_dataset.csv
│   ├── olist_order_items_dataset.csv
│   └── olist_customers_dataset.csv
├── outputs/
├── logistics_data_cleaning.py
├── requirements.txt
└── README.md
```

## Installation and execution

```bash
pip install -r requirements.txt
python logistics_data_cleaning.py
```

The script creates an `outputs` folder containing cleaned CSV files and PNG charts.

## Libraries
- pandas
- matplotlib

## Notes
Missing delivery timestamps are retained because they may indicate orders that have not been delivered. The delivery classification is based on the available actual and estimated delivery timestamps. This is an educational analysis, not a live logistics tracking system.
