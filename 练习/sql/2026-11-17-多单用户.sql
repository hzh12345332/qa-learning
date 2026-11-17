SELECT u.id,u.username,COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
GROUP BY u.id,u.username
HAVING COUNT(o.id) >= 2
ORDER BY order_count DESC;

-- 数据核对（2026-11-17）：
--   用户订单分布：1→4、2→3、3→1、4→1、5→1
--   没有 cnt=2 的用户，所以 > 和 >= 结果相同
--   但语义必须是 >= 2（边界值：恰好 2 单的用户）