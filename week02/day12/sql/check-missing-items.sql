SET NAMES utf8mb4;

-- 检查：没有明细的订单
-- 预期：订单 8（total_amount = 0）
-- 建立日期：2026-11-02
USE qa_practice;

SELECT o.id, o.total_amount, o.status
FROM orders o
LEFT JOIN order_items i ON i.order_id = o.id
WHERE i.id IS NULL;