SET NAMES utf8mb4;

-- 检查：孤儿明细（明细指向不存在的主表）
-- 预期：1 行 —— 来源=指向不存在的订单，order_id=999 那条
--       每一段都应该是 0 行才算干净
-- 建立日期：2026-11-02
USE qa_practice;

SELECT '指向不存在的订单' AS 来源, i.id, i.order_id, i.product_id, i.quantity
FROM order_items i
LEFT JOIN orders o   ON o.id = i.order_id
WHERE o.id IS NULL

UNION ALL

SELECT '指向不存在的商品', i.id, i.order_id, i.product_id, i.quantity
FROM order_items i
LEFT JOIN products p ON p.id = i.product_id
WHERE p.id IS NULL;