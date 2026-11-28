WITH cases(user_id, expected) AS (
    SELECT 1,   200 UNION ALL      -- 通过
    SELECT 2,   404 UNION ALL      -- 故意写错：实际返回 200，这条该失败
    SELECT 999, 200 UNION ALL      -- 通过
    SELECT 3,   200                -- 通过
),

results(user_id, actual) AS (
    SELECT 1,   200 UNION ALL
    SELECT 2,   200 UNION ALL
    SELECT 999, 200 UNION ALL
    SELECT 3,   200
)
SELECT COUNT(*)                                    AS "总数",
       SUM(CASE WHEN c.expected = r.actual THEN 1 ELSE 0 END) AS "通过",
       SUM(CASE WHEN c.expected != r.actual THEN 1 ELSE 0 END) AS "失败"
FROM cases c
JOIN results r ON r.user_id = c.user_id;