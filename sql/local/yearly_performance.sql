
SELECT
    STRFTIME('%Y', Order_Date) AS year,
    COUNT(DISTINCT Order_ID) AS total_orders,
    ROUND(SUM(Sales), 2) AS revenue,
    ROUND(SUM(Profit), 2) AS profit,
    ROUND(
        100.0 * SUM(Profit) / NULLIF(SUM(Sales), 0), 2
    ) AS profit_margin_pct
FROM sales_data
GROUP BY year
ORDER BY year;

