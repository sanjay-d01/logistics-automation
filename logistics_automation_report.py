import schedule
import time
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# 1. Fetch data from MySQL
def fetch_data():

    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    query = "SELECT * FROM shipments;"

    df = pd.read_sql(query, conn)

    conn.close()

    # ==========================
    # Data Scrubbing
    # ==========================

    print("Missing Values")
    print(df.isnull().sum())

    print("\nDuplicate Rows")
    print(df.duplicated().sum())

    # Remove Duplicates
    df.drop_duplicates(inplace=True)

    # Remove Extra Spaces
    df["delivery_status"] = df["delivery_status"].str.strip()
    df["warehouse"] = df["warehouse"].str.strip()
    df["shipping_mode"] = df["shipping_mode"].str.strip()

    # Convert Dates
    df["shipment_date"] = pd.to_datetime(df["shipment_date"])
    df["delivery_date"] = pd.to_datetime(df["delivery_date"])

    # Standardize Text
    df["delivery_status"] = df["delivery_status"].str.title()
    df["warehouse"] = df["warehouse"].str.title()
    df["shipping_mode"] = df["shipping_mode"].str.title()

    # ==========================
    # Data Munging
    # ==========================

    # New Column
    df["delivery_days"] = (
        df["delivery_date"] - df["shipment_date"]
    ).dt.days

    return df


# 2. Create KPI Report & Charts
def create_charts(df):

    os.makedirs("reports", exist_ok=True)

    today = datetime.now().strftime("%Y%m%d")

    # ==========================
    # KPI REPORT
    # ==========================

    print("\n========== DAILY KPI REPORT ==========\n")

    print("Total Shipments :", len(df))

    print(
        "Delivered Shipments :",
        (df["delivery_status"] == "Delivered").sum()
    )

    print(
        "Delayed Shipments :",
        (df["delivery_status"] == "Delayed").sum()
    )

    print(
        "In Transit Shipments :",
        (df["delivery_status"] == "In Transit").sum()
    )

    print(
        "Average Delivery Days :",
        round(df["delivery_days"].mean(), 2)
    )

    print(
        "Total Fuel Cost :",
        df["fuel_cost"].sum()
    )

    print(
        "Total Delivery Cost :",
        df["delivery_cost"].sum()
    )

    # ==========================
    # Chart 1
    # Delivery Status
    # ==========================

    status = df.groupby("delivery_status").size()

    plt.figure(figsize=(6, 4))

    plt.bar(status.index, status.values)

    plt.title("Delivery Status")

    plt.xlabel("Status")

    plt.ylabel("Shipments")

    plt.savefig(f"reports/delivery_status_{today}.png")

    plt.close()

    # ==========================
    # Chart 2
    # Warehouse
    # ==========================

    warehouse = df.groupby("warehouse").size()

    plt.figure(figsize=(6, 4))

    plt.bar(warehouse.index, warehouse.values)

    plt.title("Warehouse Wise Shipments")

    plt.savefig(f"reports/warehouse_{today}.png")

    plt.close()

    # ==========================
    # Chart 3
    # Shipping Mode
    # ==========================

    shipping = df.groupby("shipping_mode").size()

    plt.figure(figsize=(6, 6))

    plt.pie(
        shipping,
        labels=shipping.index,
        autopct="%1.1f%%"
    )

    plt.title("Shipping Mode")

    plt.savefig(f"reports/shipping_mode_{today}.png")

    plt.close()

    # ==========================
    # Chart 4
    # Delivery Days
    # ==========================

    days = df.groupby("delivery_days").size()

    plt.figure(figsize=(6, 4))

    plt.bar(days.index, days.values)

    plt.title("Delivery Days")

    plt.xlabel("Days")

    plt.ylabel("Shipments")

    plt.savefig(f"reports/delivery_days_{today}.png")

    plt.close()

    print("\nAll Reports Generated Successfully")


# 3. Task
def job():

    print(f"Running Dashboard at {datetime.now()}")

    data = fetch_data()

    create_charts(data)


# 4. Schedule
schedule.every().day.at("18:00").do(job)

print("Scheduler Started... Waiting for 6:00 PM")

while True:

    schedule.run_pending()

    time.sleep(60)