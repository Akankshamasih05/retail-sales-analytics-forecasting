
"""
Project: Retail Sales Analytics & Time-Series Forecasting
Developer: Akanksha Masih
Year: 2026
"""

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Retail Sales Analytics & Time-Series Forecasting",
    page_icon="📊",
    layout="wide"
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

DATABASE = ROOT / "database/retail.db"

if not DATABASE.exists():
    st.error(
        "Database not found. Run the ETL pipeline "
        "and load_to_sqlite.py first."
    )
    st.stop()


@st.cache_data
def load_data(database_version):

    with sqlite3.connect(DATABASE) as conn:
        df = pd.read_sql_query(
            "SELECT * FROM sales_data",
            conn
        )

    df["Order_Date"] = pd.to_datetime(df["Order_Date"])
    df["Year"] = df["Order_Date"].dt.year

    return df


df = load_data(DATABASE.stat().st_mtime)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("Retail Sales Analytics")

page = st.sidebar.radio(
    "Navigation",
    [
        "Executive Overview",
        "Sales Analysis",
        "Profitability Analysis",
        "Sales Forecasting"
    ]
)

years = sorted(df["Year"].unique())

selected_years = st.sidebar.multiselect(
    "Select Years",
    years,
    default=years
)

st.sidebar.divider()

st.sidebar.caption(
    "Python | Apache Beam | SQLite | "
    "SQL | Statsmodels | Streamlit"
)

st.sidebar.divider()

st.sidebar.markdown("**Developer: Akanksha Masih**")

st.sidebar.markdown(
    "[GitHub](https://github.com/Akankshamasih05)"
)

# Filter dataset

filtered = df[df["Year"].isin(selected_years)].copy()

if filtered.empty and page != "Sales Forecasting":
    st.warning("Please select at least one year.")
    st.stop()


# --------------------------------------------------
# EXECUTIVE OVERVIEW
# --------------------------------------------------

if page == "Executive Overview":

    st.title(
        "Retail Sales Analytics & Time-Series Forecasting"
    )

    st.caption(
        "Data Engineering | Business Analytics | Predictive Modeling"
    )

    # Calculate business KPIs

    revenue = filtered["Sales"].sum()
    profit = filtered["Profit"].sum()
    orders = filtered["Order_ID"].nunique()

    margin = 100 * profit / revenue if revenue else 0

    # KPI cards

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Total Revenue",
        f"${revenue:,.2f}"
    )

    c2.metric(
        "Total Profit",
        f"${profit:,.2f}"
    )

    c3.metric(
        "Total Orders",
        f"{orders:,}"
    )

    c4.metric(
        "Profit Margin",
        f"{margin:.2f}%"
    )

    st.divider()

    # Monthly revenue trend

    monthly = (
        filtered.set_index("Order_Date")
        .resample("MS")["Sales"]
        .sum()
        .reset_index()
    )

    monthly = monthly[
        monthly["Order_Date"].dt.year.isin(selected_years)
    ]

    fig = px.line(
        monthly,
        x="Order_Date",
        y="Sales",
        markers=True,
        title="Monthly Revenue Trend",
        labels={
            "Order_Date": "Month",
            "Sales": "Revenue ($)"
        }
    )

    st.plotly_chart(fig, width="stretch")

    # Yearly financial performance

    yearly = (
        filtered.groupby("Year")[["Sales", "Profit"]]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        yearly,
        x="Year",
        y=["Sales", "Profit"],
        barmode="group",
        title="Yearly Financial Performance",
        labels={
            "value": "Amount ($)",
            "variable": "Financial Metric"
        }
    )

    fig.update_xaxes(dtick=1)

    st.plotly_chart(fig, width="stretch")


# --------------------------------------------------
# SALES ANALYSIS
# --------------------------------------------------

elif page == "Sales Analysis":

    st.title("Sales Analysis")

    st.caption(
        "Transaction distribution, revenue patterns "
        "and seasonal sales trends."
    )

    # Sales distribution

    fig = px.histogram(
        filtered,
        x="Sales",
        nbins=50,
        title="Sales Distribution",
        labels={
            "Sales": "Transaction Sales ($)"
        }
    )

    st.plotly_chart(fig, width="stretch")

    # Monthly sales seasonality

    monthly = (
        filtered.set_index("Order_Date")
        .resample("MS")["Sales"]
        .sum()
    )

    monthly = monthly[
        monthly.index.year.isin(selected_years)
    ]

    seasonality = (
        monthly.groupby(monthly.index.month)
        .mean()
        .reset_index()
    )

    seasonality.columns = [
        "Month",
        "Average Sales"
    ]

    month_names = {
        1: "Jan",
        2: "Feb",
        3: "Mar",
        4: "Apr",
        5: "May",
        6: "Jun",
        7: "Jul",
        8: "Aug",
        9: "Sep",
        10: "Oct",
        11: "Nov",
        12: "Dec"
    }

    seasonality["Month"] = (
        seasonality["Month"].map(month_names)
    )

    fig = px.bar(
        seasonality,
        x="Month",
        y="Average Sales",
        title="Monthly Sales Seasonality",
        labels={
            "Average Sales": "Average Revenue ($)"
        },
        category_orders={
            "Month": list(month_names.values())
        }
    )

    st.plotly_chart(fig, width="stretch")

    # Descriptive statistics

    st.subheader("Descriptive Statistics")

    st.dataframe(
        filtered[
            ["Sales", "Profit", "Quantity"]
        ].describe().round(2),
        width="stretch"
    )


# --------------------------------------------------
# PROFITABILITY ANALYSIS
# --------------------------------------------------

elif page == "Profitability Analysis":

    st.title("Profitability Analysis")

    st.caption(
        "Analyze financial performance and "
        "identify loss-making transactions."
    )

    # Sales versus profit

    fig = px.scatter(
        filtered,
        x="Sales",
        y="Profit",
        color=filtered["Year"].astype(str),
        title="Sales vs Profit",
        labels={
            "Sales": "Sales ($)",
            "Profit": "Profit ($)",
            "color": "Year"
        }
    )

    fig.add_hline(
        y=0,
        line_dash="dash"
    )

    st.plotly_chart(fig, width="stretch")

    # Identify loss-making transactions

    loss_orders = filtered[
        filtered["Profit"] < 0
    ]

    loss_rate = (
        100 * len(loss_orders) / len(filtered)
        if len(filtered) else 0
    )

    correlation = filtered["Sales"].corr(
        filtered["Profit"]
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Loss-Making Transactions",
        f"{len(loss_orders):,}"
    )

    c2.metric(
        "Total Transaction Losses",
        f"${loss_orders['Profit'].sum():,.2f}"
    )

    c3.metric(
        "Loss-Making Transaction Rate",
        f"{loss_rate:.2f}%"
    )

    c4.metric(
        "Sales-Profit Correlation",
        f"{correlation:.3f}"
    )

    st.divider()

    st.subheader(
        "Top 20 Loss-Making Transactions"
    )

    st.dataframe(
        loss_orders.sort_values("Profit").head(20),
        width="stretch",
        hide_index=True
    )


# --------------------------------------------------
# SALES FORECASTING
# --------------------------------------------------

elif page == "Sales Forecasting":

    st.title(
        "Sales Forecasting and Model Evaluation"
    )

    st.caption(
        "Statistical forecasting, baseline benchmarking "
        "and time-series validation."
    )

    st.info(
        "Forecast evaluation uses the full historical "
        "dataset, independently of the year filter."
    )

    forecast_dir = ROOT / "output/forecasting"

    required_files = [
        forecast_dir / "model_comparison.csv",
        forecast_dir / "forecast_comparison.csv",
        forecast_dir / "backtesting_summary.csv"
    ]

    if not all(file.exists() for file in required_files):

        st.error(
            "Forecasting results are missing. "
            "Run the forecasting and backtesting scripts first."
        )

        st.code(
            "python models/sales_forecasting.py\n"
            "python models/backtesting.py",
            language="bash"
        )

        st.stop()

    # Load forecasting results

    metrics = pd.read_csv(
        forecast_dir / "model_comparison.csv"
    )

    predictions = pd.read_csv(
        forecast_dir / "forecast_comparison.csv"
    )

    backtesting = pd.read_csv(
        forecast_dir / "backtesting_summary.csv"
    )

    # Best-performing models

    best_holdout = metrics.sort_values(
        "MAE"
    ).iloc[0]

    best_backtest = backtesting.sort_values(
        "MAE"
    ).iloc[0]

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Best Holdout Model",
        best_holdout["Model"]
    )

    c2.metric(
        "Holdout WAPE",
        f"{best_holdout['WAPE (%)']:.2f}%"
    )

    c3.metric(
        "Best Backtesting Model",
        best_backtest["Model"]
    )

    c4.metric(
        "Backtesting MAE",
        f"${best_backtest['MAE']:,.2f}"
    )

    st.divider()

    # Holdout evaluation

    st.subheader("12-Month Holdout Evaluation")

    st.caption(
        "Training: January 2014 – December 2016 | "
        "Testing: January 2017 – December 2017"
    )

    st.dataframe(
        metrics.round(2),
        width="stretch",
        hide_index=True
    )

    fig = px.bar(
        metrics,
        x="Model",
        y="MAE",
        color="Model",
        title="Holdout Forecasting Error",
        labels={
            "MAE": "Mean Absolute Error ($)"
        }
    )

    st.plotly_chart(fig, width="stretch")

    # Actual versus predicted sales

    st.subheader("Actual vs Predicted Sales")

    date_column = predictions.columns[0]

    predictions[date_column] = pd.to_datetime(
        predictions[date_column]
    )

    fig = px.line(
        predictions,
        x=date_column,
        y=[
            "Actual",
            "Seasonal_Naive",
            "Holt_Winters",
            "SARIMA"
        ],
        markers=True,
        labels={
            date_column: "Month",
            "value": "Revenue ($)",
            "variable": "Model"
        }
    )

    st.plotly_chart(fig, width="stretch")

    st.divider()

    # Cross-validation

    st.subheader(
        "Expanding-Window Cross-Validation"
    )

    st.caption(
        "Four chronological validation folds "
        "using a six-month forecast horizon."
    )

    st.dataframe(
        backtesting.round(2),
        width="stretch",
        hide_index=True
    )

    metric = st.selectbox(
        "Select Evaluation Metric",
        [
            "MAE",
            "RMSE",
            "WAPE (%)"
        ]
    )

    fig = px.bar(
        backtesting,
        x="Model",
        y=metric,
        color="Model",
        title=f"Cross-Validation: {metric}"
    )

    st.plotly_chart(fig, width="stretch")

    # Baseline improvement

    baseline = backtesting[
        backtesting["Model"] == "Seasonal Naive"
    ]

    if not baseline.empty:

        baseline_mae = baseline.iloc[0]["MAE"]

        if baseline_mae > 0:

            improvement = (
                100
                * (baseline_mae - best_backtest["MAE"])
                / baseline_mae
            )

            st.success(
                f"{best_backtest['Model']} achieved "
                f"{improvement:.2f}% lower average MAE "
                "than the Seasonal Naive baseline "
                "during cross-validation."
            )

    # Evaluation limitations

    with st.expander("Model Evaluation Notes"):

        st.markdown(
            """
            - The dataset contains 48 monthly observations.
            - Holdout evaluation uses a 12-month horizon.
            - Cross-validation uses a 6-month horizon.
            - The evaluation periods overlap.
            - SARIMA parameters were not extensively optimized.
            - Results represent historical forecasting evaluation,
              not live future-period predictions.
            """
        )
