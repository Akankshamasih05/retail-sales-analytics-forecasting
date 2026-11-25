
"""
Retail Sales Analytics & Time-Series Forecasting
Developer: Akanksha Masih
Year: 2026

Local retail data ingestion and transformation pipeline.
"""

import csv
import json
import math
import apache_beam as beam

from datetime import date
from pathlib import Path
from apache_beam.options.pipeline_options import PipelineOptions


ROOT = Path(__file__).resolve().parents[1]

INPUT = ROOT / "data/stores_sales_forecasting.csv"
OUTPUT = ROOT / "output/cleaned_sales"


def read_records(path):
    """Read structured records from the source CSV."""

    with open(path, encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for record in reader:
            yield {
                key.strip().replace(" ", "_").lower(): value
                for key, value in record.items()
                if key is not None
            }


def transform(record):
    """Validate and transform a retail transaction."""

    sales = float(record["sales"])
    profit = float(record["profit"])
    quantity = int(record["quantity"])

    order_date = date.fromisoformat(
        record["order_date"]
    )

    ship_date = date.fromisoformat(
        record["ship_date"]
    )

    if not all(math.isfinite(v) for v in [sales, profit]):
        raise ValueError("Invalid numeric value")

    if quantity <= 0:
        raise ValueError("Invalid transaction quantity")

    if ship_date < order_date:
        raise ValueError("Shipping date precedes order date")

    margin = profit / sales if sales != 0 else 0.0

    return {
        "Row_ID": record["row_id"],
        "Order_ID": record["order_id"],
        "Order_Date": order_date.isoformat(),
        "Ship_Date": ship_date.isoformat(),
        "Sales": sales,
        "Quantity": quantity,
        "Profit": profit,
        "Profit_Margin": margin
    }


def main():

    if not INPUT.exists():
        raise FileNotFoundError(
            f"Source dataset not found: {INPUT}"
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    records = list(read_records(INPUT))

    print(f"Source records: {len(records)}")

    options = PipelineOptions(
        runner="DirectRunner"
    )

    with beam.Pipeline(options=options) as pipeline:

        (
            pipeline
            | "Ingest Transactions" >> beam.Create(records)
            | "Transform Transactions" >> beam.Map(transform)
            | "Serialize Records" >> beam.Map(json.dumps)
            | "Export Dataset" >> beam.io.WriteToText(
                str(OUTPUT),
                file_name_suffix=".jsonl",
                num_shards=1
            )
        )

    print("ETL pipeline completed successfully.")


if __name__ == "__main__":
    main()
