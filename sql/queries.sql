-- 1. Total Net Revenue by Month
SELECT strftime('%Y-%m', order_timestamp) as month, SUM(net_revenue) FROM delivered_revenue GROUP BY 1 ORDER BY 1;

-- 2. Top 5 Products by Revenue
SELECT p.product_name, SUM(oi.quantity * oi.unit_price * (1 - COALESCE(o.discount_pct, 0)/100.0)) as revenue
FROM orders o JOIN order_items oi ON o.order_id = oi.order_id JOIN products p ON oi.product_id = p.product_id
WHERE o.status = 'delivered' GROUP BY 1 ORDER BY 2 DESC LIMIT 5;

-- 3. Sales by Country
SELECT country, SUM(net_revenue) as rev FROM delivered_revenue GROUP BY 1 ORDER BY 2 DESC;

-- 4. Sales by Channel
SELECT channel, SUM(net_revenue) as rev FROM delivered_revenue GROUP BY 1 ORDER BY 2 DESC;

-- 5. Average Order Value (AOV)
SELECT AVG(order_total) FROM (SELECT order_id, SUM(net_revenue) as order_total FROM delivered_revenue GROUP BY 1);

-- 6. Repeat Purchase Rate
WITH CustomerOrders AS (SELECT customer_id, COUNT(DISTINCT order_id) as orders FROM orders GROUP BY 1)
SELECT CAST(SUM(CASE WHEN orders > 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) as repeat_rate FROM CustomerOrders;

-- 7. Monthly Customer Acquisition Cost (CAC)
SELECT m.month, m.channel, m.spend, COUNT(DISTINCT c.customer_id) as new_customers, (m.spend / COUNT(DISTINCT c.customer_id)) as CAC
FROM marketing_spend m LEFT JOIN customers c ON strftime('%Y-%m', c.signup_date) = strftime('%Y-%m', m.month||'-01') AND m.channel = c.acquisition_channel GROUP BY 1, 2;

-- 8. Refund Rate by Category
SELECT p.category, SUM(CASE WHEN o.status = 'returned' THEN 1 ELSE 0 END)*100.0 / COUNT(*) as return_pct
FROM orders o JOIN order_items oi ON o.order_id = oi.order_id JOIN products p ON oi.product_id = p.product_id GROUP BY 1;

-- 9. Revenue Month-over-Month Growth
WITH Monthly AS (SELECT strftime('%Y-%m', order_timestamp) as m, SUM(net_revenue) as rev FROM delivered_revenue GROUP BY 1)
SELECT m, rev, ((rev - LAG(rev) OVER (ORDER BY m)) / LAG(rev) OVER (ORDER BY m)) * 100 as mom_pct FROM Monthly;

-- 10. Best Selling Category per Season (Winter vs Summer)
SELECT CASE WHEN strftime('%m', order_timestamp) IN ('12','01','02') THEN 'Winter' ELSE 'Other' END as season, category, SUM(net_revenue)
FROM delivered_revenue GROUP BY 1, 2 ORDER BY 1, 3 DESC;