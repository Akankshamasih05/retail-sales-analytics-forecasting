
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error

OUTPUT = Path("output/forecasting")
OUTPUT.mkdir(parents=True, exist_ok=True)

# 1. Load data
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

print("Monthly observations:", len(monthly))

# 2. Chronological train-test split
TEST_SIZE = 12

train = monthly.iloc[:-TEST_SIZE]
test = monthly.iloc[-TEST_SIZE:]

if len(train) < 24:
    raise ValueError(
        "At least 24 training months are required."
    )

print("\nTraining period:")
print(train.index.min(), "to", train.index.max())

print("\nTesting period:")
print(test.index.min(), "to", test.index.max())

# 3. Seasonal Naive baseline
naive = pd.Series(
    train.iloc[-12:].values,
    index=test.index
)

# 4. Holt-Winters
hw_model = ExponentialSmoothing(
    train,
    trend="add",
    seasonal="add",
    seasonal_periods=12
).fit()

hw_forecast = hw_model.forecast(TEST_SIZE)

# 5. SARIMA
sarima_model = SARIMAX(
    train,
    order=(1, 1, 1),
    seasonal_order=(1, 0, 0, 12)
).fit(disp=False)

sarima_forecast = sarima_model.forecast(TEST_SIZE)

# 6. Evaluate models
predictions = {
    "Seasonal Naive": naive,
    "Holt-Winters": hw_forecast,
    "SARIMA": sarima_forecast
}

results = []

for name, pred in predictions.items():

    mae = mean_absolute_error(test, pred)

    rmse = np.sqrt(
        mean_squared_error(test, pred)
    )

    denominator = np.abs(test).sum()

    wape = (
        100 * np.abs(test - pred).sum() / denominator
        if denominator != 0 else np.nan
    )

    results.append({
        "Model": name,
        "MAE": mae,
        "RMSE": rmse,
        "WAPE (%)": wape
    })

metrics = pd.DataFrame(results).sort_values("MAE")

print("\nMODEL PERFORMANCE")
print(metrics.round(2).to_string(index=False))

metrics.to_csv(
    OUTPUT / "model_comparison.csv",
    index=False
)

# 7. Save predictions
comparison = pd.DataFrame({
    "Actual": test,
    "Seasonal_Naive": naive,
    "Holt_Winters": hw_forecast,
    "SARIMA": sarima_forecast
})

comparison.to_csv(
    OUTPUT / "forecast_comparison.csv"
)

# 8. Plot model predictions
plt.figure(figsize=(14, 6))

plt.plot(train.index, train, label="Training Data")
plt.plot(test.index, test, label="Actual Sales",
         color="black", linewidth=2)

for name, pred in predictions.items():
    plt.plot(
        pred.index,
        pred,
        linestyle="--",
        label=name
    )

plt.axvline(
    test.index[0],
    color="gray",
    linestyle=":"
)

plt.title("Retail Sales Forecasting - Model Comparison")
plt.xlabel("Date")
plt.ylabel("Monthly Revenue ($)")
plt.legend()
plt.tight_layout()

plt.savefig(
    OUTPUT / "forecast_comparison.png",
    dpi=150
)

plt.close()

print("\nBest model by holdout MAE:",
      metrics.iloc[0]["Model"])

print("\nForecasting completed successfully!")
