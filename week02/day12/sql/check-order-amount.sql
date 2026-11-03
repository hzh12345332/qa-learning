SET NAMES utf8mb4;

-- 检查：订单金额 ≠ 明细合计
-- 预期：订单 1、2、7
-- 建立日期：2026-11-02
USE qa_practice;

SELECT o.id,
       o.total_amount                AS 账面,
       SUM(i.quantity * i.unit_price) AS 明细合计,
       o.total_amount - SUM(i.quantity * i.unit_price) AS 差异
FROM orders o
JOIN order_items i ON i.order_id = o.id
GROUP BY o.id, o.total_amount
HAVING o.total_amount <> SUM(i.quantity * i.unit_price);