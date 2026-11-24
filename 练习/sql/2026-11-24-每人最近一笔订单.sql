WITH t(user_id, order_id, amount, created_at) AS (
    SELECT 1, 101, 50.00, '2026-11-01' UNION ALL
    SELECT 1, 102, 80.00, '2026-11-05' UNION ALL
    SELECT 2, 201, 30.00, '2026-11-03' UNION ALL
    SELECT 2, 202, 20.00, '2026-11-09' UNION ALL
    SELECT 3, 301, 99.00, '2026-11-07'
),
ranked AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn
    FROM t
)
SELECT user_id, order_id, amount, created_at
FROM ranked
WHERE rn = 1;