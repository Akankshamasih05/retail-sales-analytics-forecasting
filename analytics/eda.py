
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

OUTPUT = Path("output/visualizations")
OUTPUT.mkdir(parents=True, exist_ok=True)

# Load data from SQLite
with sqlite3.connect("database/retail.db") as conn:
    df = pd.read_sql_query("SELECT * FROM sales_data", conn)

df["Order_Date"] = pd.to_datetime(df["Order_Date"])

plt.style.use("ggplot")

# 1. Monthly sales trend
monthly = df.set_index("Order_Date").resample("MS")["Sales"].sum()

plt.figure(figsize=(12, 5))
plt.plot(monthly.index, monthly.values, marker="o", markersize=3)
plt.title("Monthly Retail Sales Trend")
plt.xlabel("Date")
plt.ylabel("Revenue ($)")
plt.tight_layout()
plt.savefig(OUTPUT / "monthly_sales.png", dpi=150)
plt.close()

# 2. Yearly revenue and profit
df["Year"] = df["Order_Date"].dt.year

yearly = df.groupby("Year")[["Sales", "Profit"]].sum()

yearly.plot(kind="bar", subplots=True, figsize=(10, 7))
plt.suptitle("Yearly Revenue and Profit")
plt.tight_layout()
plt.savefig(OUTPUT / "yearly_performance.png", dpi=150)
plt.close()

# 3. Sales distribution
plt.figure(figsize=(10, 5))
plt.hist(df["Sales"], bins=50, edgecolor="white")
plt.title("Sales Distribution")
plt.xlabel("Transaction Sales ($)")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig(OUTPUT / "sales_distribution.png", dpi=150)
plt.close()

# 4. Monthly seasonality
seasonality = monthly.groupby(monthly.index.month).mean()

plt.figure(figsize=(10, 5))
plt.bar(seasonality.index, seasonality.values)
plt.xticks(range(1, 13))
plt.title("Average Monthly Revenue by Calendar Month")
plt.xlabel("Month")
plt.ylabel("Average Revenue ($)")
plt.tight_layout()
plt.savefig(OUTPUT / "seasonality.png", dpi=150)
plt.close()

# 5. Sales vs Profit
plt.figure(figsize=(10, 5))
plt.scatter(df["Sales"], df["Profit"], alpha=0.4)
plt.axhline(0, linestyle="--", color="black")
plt.title("Relationship Between Sales and Profit")
plt.xlabel("Sales ($)")
plt.ylabel("Profit ($)")
plt.tight_layout()
plt.savefig(OUTPUT / "sales_vs_profit.png", dpi=150)
plt.close()

# Statistical summary
print("\nDescriptive Statistics:")
print(df[["Sales", "Profit", "Quantity"]].describe())

print("\nSales-Profit Correlation:")
print(df["Sales"].corr(df["Profit"]))

print("\nDate Range:")
print(df["Order_Date"].min(), "to", df["Order_Date"].max())

print("\nMonthly Observations:", len(monthly))

print("\nAll EDA visualizations saved successfully!")
