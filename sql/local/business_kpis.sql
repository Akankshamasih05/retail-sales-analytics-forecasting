
SELECT
    COUNT(*) AS total_transactions,
    COUNT(DISTINCT Order_ID) AS total_orders,
    ROUND(SUM(Sales), 2) AS total_revenue,
    ROUND(SUM(Profit), 2) AS total_profit,
    SUM(Quantity) AS total_units_sold,
    ROUND(
        SUM(Sales) / COUNT(DISTINCT Order_ID), 2
    ) AS average_order_value,
    ROUND(
        100.0 * SUM(Profit) / NULLIF(SUM(Sales), 0), 2
    ) AS profit_margin_pct
FROM sales_data;
