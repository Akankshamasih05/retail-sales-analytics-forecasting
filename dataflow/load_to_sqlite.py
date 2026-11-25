
import pandas as pd
import sqlite3
from pathlib import Path

# Load cleaned data
df = pd.read_json(
    "output/cleaned_sales-00000-of-00001.jsonl",
    lines=True
)

# Create database folder
Path("database").mkdir(exist_ok=True)

# Connect to SQLite database
with sqlite3.connect("database/retail.db") as conn:

    df.to_sql(
        "sales_data",
        conn,
        if_exists="replace",
        index=False
    )

    result = pd.read_sql_query(
        "SELECT COUNT(*) AS total_records FROM sales_data",
        conn
    )

    print(result)

print("Database created successfully!")
