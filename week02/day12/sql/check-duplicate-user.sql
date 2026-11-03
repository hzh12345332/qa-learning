SET NAMES utf8mb4;

-- 检查：重名用户（username 没有 UNIQUE，允许重名）
-- 预期：张三丰 ×2
-- 建立日期：2026-11-02
USE qa_practice;

SELECT username, COUNT(*) AS 条数, GROUP_CONCAT(phone) AS 手机号
FROM users
GROUP BY username
HAVING COUNT(*) > 1;