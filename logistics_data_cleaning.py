"""
Week 1: Data Collection and Cleaning Strategies in Logistics
Dataset: Olist Brazilian E-Commerce Public Dataset

Expected input files in the data/ folder:
- olist_orders_dataset.csv
- olist_order_items_dataset.csv
- olist_customers_dataset.csv

Run:
    pip install -r requirements.txt
    python logistics_data_cleaning.py
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# -------------------- 1. PATHS --------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

ORDERS_FILE = DATA_DIR / "olist_orders_dataset.csv"
ITEMS_FILE = DATA_DIR / "olist_order_items_dataset.csv"
CUSTOMERS_FILE = DATA_DIR / "olist_customers_dataset.csv"


def load_data():
    """Load the three Olist CSV files."""
    orders = pd.read_csv(ORDERS_FILE)
    items = pd.read_csv(ITEMS_FILE)
    customers = pd.read_csv(CUSTOMERS_FILE)

    print("Orders shape:", orders.shape)
    print("Items shape:", items.shape)
    print("Customers shape:", customers.shape)
    return orders, items, customers


# -------------------- 2. DATA INSPECTION --------------------
def inspect_data(dataframes, names):
    for name, df in zip(names, dataframes):
        print(f"\n--- {name} ---")
        print(df.head())
        print("\nData types:\n", df.dtypes)
        print("\nMissing values:\n", df.isnull().sum())
        print("Duplicate rows:", df.duplicated().sum())


# -------------------- 3. DATA CLEANING --------------------
def clean_data(orders, items, customers):
    # Remove duplicate rows
    orders = orders.drop_duplicates().copy()
    items = items.drop_duplicates().copy()
    customers = customers.drop_duplicates().copy()

    # Convert order date columns to datetime
    date_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
    for column in date_columns:
        if column in orders.columns:
            orders[column] = pd.to_datetime(orders[column], errors="coerce")

    # Standardize text columns
    for df in (orders, items, customers):
        text_columns = df.select_dtypes(include="object").columns
        for column in text_columns:
            df[column] = df[column].str.strip()

    # Do not delete orders with missing delivery dates:
    # these may represent orders that were not delivered.
    return orders, items, customers


# -------------------- 4. DATA INTEGRATION --------------------
def integrate_data(orders, items, customers):
    # Attach customer information to orders
    integrated = orders.merge(
        customers,
        on="customer_id",
        how="left",
        suffixes=("", "_customer"),
    )

    # Attach item information to each order
    integrated = integrated.merge(
        items,
        on="order_id",
        how="left",
        suffixes=("", "_item"),
    )

    print("\nIntegrated dataset shape:", integrated.shape)
    return integrated


# -------------------- 5. LOGISTICS METRICS --------------------
def calculate_delivery_performance(orders):
    result = orders.copy()

    delivered = result["order_delivered_customer_date"].notna()
    result["delivery_status"] = "Unknown / Not Delivered"
    result.loc[delivered, "delivery_status"] = "On Time"

    late = (
        delivered
        & (
            result["order_delivered_customer_date"]
            > result["order_estimated_delivery_date"]
        )
    )
    result.loc[late, "delivery_status"] = "Late"

    result["delivery_days"] = (
        result["order_delivered_customer_date"]
        - result["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400

    print("\nDelivery status counts:")
    print(result["delivery_status"].value_counts(dropna=False))
    return result


# -------------------- 6. VISUALIZATIONS --------------------
def create_visualizations(orders, items, integrated):
    # Chart 1: Dataset dimensions
    names = ["Orders", "Items", "Customers", "Integrated"]
    # Integrated row count is used here as an overview of the merged data.
    sizes = [len(orders), len(items), len(pd.read_csv(CUSTOMERS_FILE)), len(integrated)]
    plt.figure(figsize=(8, 5))
    plt.bar(names, sizes)
    plt.title("Dataset Dimensions")
    plt.ylabel("Number of Rows")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "dataset_dimensions.png", dpi=150)
    plt.close()

    # Chart 2: Delivery status
    status_counts = orders["delivery_status"].value_counts()
    plt.figure(figsize=(8, 5))
    status_counts.plot(kind="bar")
    plt.title("Delivery Performance")
    plt.xlabel("Delivery Status")
    plt.ylabel("Number of Orders")
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "delivery_performance.png", dpi=150)
    plt.close()

    # Chart 3: Freight cost distribution
    if "freight_value" in items.columns:
        plt.figure(figsize=(8, 5))
        items["freight_value"].dropna().plot(kind="hist", bins=30)
        plt.title("Freight Cost Distribution")
        plt.xlabel("Freight Value")
        plt.ylabel("Frequency")
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "freight_cost_distribution.png", dpi=150)
        plt.close()

    # Chart 4: Missing values in orders
    missing = orders.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=False)
    if not missing.empty:
        plt.figure(figsize=(10, 5))
        missing.plot(kind="bar")
        plt.title("Missing Values by Orders Column")
        plt.xlabel("Column")
        plt.ylabel("Missing Values")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "missing_values_orders.png", dpi=150)
        plt.close()

    # Chart 5: Monthly order volume
    monthly = (
        orders.dropna(subset=["order_purchase_timestamp"])
        .set_index("order_purchase_timestamp")
        .resample("ME")["order_id"]
        .count()
    )
    plt.figure(figsize=(10, 5))
    monthly.plot()
    plt.title("Monthly Order Volume")
    plt.xlabel("Month")
    plt.ylabel("Number of Orders")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "monthly_order_volume.png", dpi=150)
    plt.close()


# -------------------- 7. EXPORT --------------------
def main():
    orders, items, customers = load_data()

    inspect_data(
        [orders, items, customers],
        ["Orders", "Order Items", "Customers"],
    )

    orders, items, customers = clean_data(orders, items, customers)
    orders = calculate_delivery_performance(orders)
    integrated = integrate_data(orders, items, customers)

    # Save cleaned and integrated datasets
    orders.to_csv(OUTPUT_DIR / "cleaned_orders.csv", index=False)
    items.to_csv(OUTPUT_DIR / "cleaned_order_items.csv", index=False)
    customers.to_csv(OUTPUT_DIR / "cleaned_customers.csv", index=False)
    integrated.to_csv(OUTPUT_DIR / "integrated_logistics_dataset.csv", index=False)

    create_visualizations(orders, items, integrated)

    print("\nProcess completed successfully.")
    print("Cleaned datasets and charts are saved in the outputs/ folder.")


if __name__ == "__main__":
    main()
