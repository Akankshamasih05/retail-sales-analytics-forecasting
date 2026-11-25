
import sqlite3
import pandas as pd
import numpy as np

from pathlib import Path
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error

OUTPUT = Path("output/forecasting")
OUTPUT.mkdir(parents=True, exist_ok=True)

# Load monthly sales
with sqlite3.connect("database/retail.db") as conn:
    df = pd.read_sql_query(
        "SELECT Order_Date, Sales FROM sales_data",
        conn
    )

df["Order_Date"] = pd.to_datetime(df["Order_Date"])

monthly = (
    df.set_index("Order_Date")
    .resample("MS")["Sales"]
    .sum()
)

# Cross-validation configuration
INITIAL_TRAIN = 24
FORECAST_HORIZON = 6
STEP = 6

results = []

for end in range(
    INITIAL_TRAIN,
    len(monthly) - FORECAST_HORIZON + 1,
    STEP
):

    train = monthly.iloc[:end]
    test = monthly.iloc[end:end + FORECAST_HORIZON]

    print(f"\nTraining ends: {train.index[-1]}")
    print(f"Validation starts: {test.index[0]}")

    # Seasonal Naive
    naive = train.iloc[-12:-6].values

    # Holt-Winters
    hw = ExponentialSmoothing(
        train,
        trend="add",
        seasonal="add",
        seasonal_periods=12
    ).fit().forecast(FORECAST_HORIZON)

    # SARIMA
    sarima = SARIMAX(
        train,
        order=(1, 1, 1),
        seasonal_order=(1, 0, 0, 12)
    ).fit(disp=False).forecast(FORECAST_HORIZON)

    predictions = {
        "Seasonal Naive": naive,
        "Holt-Winters": hw,
        "SARIMA": sarima
    }

    for name, pred in predictions.items():

        actual = test.to_numpy()
        predicted = np.asarray(pred)

        mae = mean_absolute_error(actual, predicted)

        rmse = np.sqrt(
            mean_squared_error(actual, predicted)
        )

        denominator = np.abs(actual).sum()

        wape = (
            100 * np.abs(actual - predicted).sum()
            / denominator
            if denominator > 0 else np.nan
        )

        results.append({
            "Model": name,
            "Training_End": train.index[-1],
            "Validation_Start": test.index[0],
            "MAE": mae,
            "RMSE": rmse,
            "WAPE (%)": wape
        })

results_df = pd.DataFrame(results)

summary = (
    results_df.groupby("Model")[["MAE", "RMSE", "WAPE (%)"]]
    .mean()
    .sort_values("MAE")
)

results_df.to_csv(
    OUTPUT / "backtesting_results.csv",
    index=False
)

summary.to_csv(
    OUTPUT / "backtesting_summary.csv"
)

print("\nCROSS-VALIDATION RESULTS")
print(summary.round(2))

print("\nBest model:", summary.index[0])

print("\nBacktesting completed successfully!")
