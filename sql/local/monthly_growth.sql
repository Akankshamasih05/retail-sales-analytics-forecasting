
WITH monthly_sales AS (
    SELECT
        STRFTIME('%Y-%m', Order_Date) AS month,
        SUM(Sales) AS revenue,
        SUM(Profit) AS profit
    FROM sales_data
    GROUP BY STRFTIME('%Y-%m', Order_Date)
),
growth AS (
    SELECT
        month,
        revenue,
        profit,
        LAG(revenue) OVER (
            ORDER BY month
        ) AS previous_month_revenue
    FROM monthly_sales
)
SELECT
    month,
    ROUND(revenue, 2) AS revenue,
    ROUND(profit, 2) AS profit,
    ROUND(previous_month_revenue, 2) AS previous_revenue,
    ROUND(
        100.0 * (revenue - previous_month_revenue)
        / NULLIF(previous_month_revenue, 0), 2
    ) AS growth_pct
FROM growth
ORDER BY month;
