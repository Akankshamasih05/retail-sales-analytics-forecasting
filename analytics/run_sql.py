
import sqlite3
import pandas as pd
from pathlib import Path

DATABASE = "database/retail.db"
SQL_FOLDER = Path("sql/local")
OUTPUT_FOLDER = Path("output/analytics")

OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

with sqlite3.connect(DATABASE) as conn:

    for sql_file in sorted(SQL_FOLDER.glob("*.sql")):

        print(f"\n{'=' * 60}")
        print(f"Analysis: {sql_file.stem}")
        print("=" * 60)

        query = sql_file.read_text()

        result = pd.read_sql_query(query, conn)

        print(result.to_string(index=False))

        output_file = OUTPUT_FOLDER / f"{sql_file.stem}.csv"

        result.to_csv(output_file, index=False)

        print(f"\nResults saved to: {output_file}")

print("\nAll SQL analyses completed successfully!")
