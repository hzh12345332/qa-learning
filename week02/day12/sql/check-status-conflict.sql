SET NAMES utf8mb4;

-- 检查：状态与数据自相矛盾
-- 预期：1 行 —— 规则=已取消却有明细，订单 4
--       三条规则各自都应该是 0 行
-- 建立日期：2026-11-02
USE qa_practice;

-- 规则 1：已支付(status=1) 但金额为 0
SELECT '已支付但金额为0' AS 规则, o.id AS 订单号, o.total_amount AS 金额,
       o.status AS 状态, NULL AS 明细数
FROM orders o
WHERE o.status = 1 AND o.total_amount = 0

UNION ALL

-- 规则 2：已取消(status=2) 却还有明细
SELECT '已取消却有明细', o.id, o.total_amount, o.status, COUNT(i.id)
FROM orders o
JOIN order_items i ON i.order_id = o.id
WHERE o.status = 2
GROUP BY o.id, o.total_amount, o.status

UNION ALL

-- 规则 3：金额为 0 但有明细
SELECT '金额为0但有明细', o.id, o.total_amount, o.status, COUNT(i.id)
FROM orders o
JOIN order_items i ON i.order_id = o.id
WHERE o.total_amount = 0
GROUP BY o.id, o.total_amount, o.status;