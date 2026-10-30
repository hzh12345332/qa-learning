# Day 11 ｜ SQL 基础

## 一、环境与连接

### 1.1 本地 MySQL 连接方式（命令行 + Navicat）

- mysql -u root -p

### 1.2 5 个元命令

| 命令 | 作用 |
| --- | --- |
| SHOW DATABASES; | 列出所有库 |
| USE qa_practice; | 切到某个库（后面所有表操作都在这个库里） |
| SHOW TABLES; | 列出当前库的表 |
| DESC users; | 看表结构（字段/类型/约束） |
| SHOW CREATE TABLE users\G | 看建表语句原文（\G 让结果竖排，好读） |
| exit 或 \q | 退出 |

### 1.3 我踩的坑（分号 / -> 提示符 / 编码）

- 最大的坑：SQL 语句没写分号时，提示符会变成 ->，一直在等你补。看到 -> 就说明上一条没结束，补个 ; 或者按 Ctrl+C 放弃。

## 二、库表结构

### 2.1 建库语句（字符集为什么必须 utf8mb4）

```
DROP DATABASE IF EXISTS qa_practice;      -- 反复练习用，先删后建
CREATE DATABASE qa_practice
  DEFAULT CHARACTER SET utf8mb4           -- 一定要 utf8mb4，utf8 存不了 emoji
  COLLATE utf8mb4_0900_ai_ci;
USE qa_practice;
```

### 2.2 数据类型选择表

| 存什么 | 用哪个 | 为什么 |
| --- | --- | --- |
| 整数 id / 数量 | INT | 数字 |
| 金额 | DECIMAL(10,2) | 绝不能用 FLOAT/DOUBLE（0.1+0.2 ≠ 0.3，对账会差几分钱） |
| 短文本 | VARCHAR(50) | 长度按实际给，别一律 255 |
| 长文本（备注、日志） | TEXT | 变长存储；查询时别全量取出 |
| 时间 | DATETIME | 5 字节，范围到 9999 年；TIMESTAMP 只到 2038 且受时区影响 |
| 是/否、状态枚举 | TINYINT + COMMENT | 比 VARCHAR 省空间，也方便比较 |
| 布尔 | TINYINT(1) | MySQL 没有真正的 BOOLEAN，BOOL 只是 TINYINT(1) 的别名 |

### 2.3 约束清单（含"测试视角"一列：每条约束该测什么）

| 约束 | 作用 | 测试视角（重要） |
| --- | --- | --- |
| PRIMARY KEY | 唯一 + 非空，一行一个 | 主键重复必然插入失败 → 要测报错 |
| AUTO_INCREMENT | 自动递增，插入时不要手写 id | 手写 id 会造成后续自增冲突 |
| NOT NULL | 不许为空 | 空值插入应被拒绝 |
| UNIQUE | 不许重复 | 重复手机号应被拒绝 |
| DEFAULT | 不填时的默认值 | 不填字段时验默认值对不对 |
| FOREIGN KEY | 必须指向父表存在的 id | 插入不存在的 user_id 应失败 |

### 2.4 四张表的建表语句（我自己跑过的那一版）

- 用户

```
CREATE TABLE users (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  username   VARCHAR(50)  NOT NULL,
  phone      VARCHAR(20)  NOT NULL UNIQUE,
  status     TINYINT      NOT NULL DEFAULT 1 COMMENT '1=正常 0=禁用',
  created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
```

- 商品

```
CREATE TABLE products (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  name       VARCHAR(100)  NOT NULL,
  price      DECIMAL(10,2) NOT NULL,
  stock      INT           NOT NULL DEFAULT 0,
  created_at DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
```

- 订单

```
CREATE TABLE orders (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  user_id      INT           NOT NULL,
  total_amount DECIMAL(10,2) NOT NULL,
  status       TINYINT       NOT NULL DEFAULT 0 COMMENT '0=待支付 1=已支付 2=已取消',
  created_at   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_user (user_id),
  CONSTRAINT fk_orders_user FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB;
```

- 订单明细

```
CREATE TABLE order_items (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  order_id   INT           NOT NULL,
  product_id INT           NOT NULL,
  quantity   INT           NOT NULL,
  unit_price DECIMAL(10,2) NOT NULL,
  KEY idx_order (order_id),
  CONSTRAINT fk_items_order   FOREIGN KEY (order_id)   REFERENCES orders(id),
  CONSTRAINT fk_items_product FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB;
```

### 2.5 建表失败的记录（外键顺序之类）

**顺序不能乱**：`users` / `products` → `orders` → `order_items`。先建带外键的子表会报：

```
ERROR 1215 (HY000): Cannot add foreign key constraint
-- 或 errno: 150 "Foreign key constraint is incorrectly formed"
```

这个报错文案很烂，它把五种原因混在一起：

| 真实原因 | 怎么查 |
| --- | --- |
| 父表不存在 / 名字打错 | `SHOW TABLES;` |
| 被引用的列没索引 | `SHOW CREATE TABLE users\G` 看有没有 PRIMARY KEY |
| **两边类型不一致**（最常见） | 逐字比对两个字段的定义 |
| 字符集 / 排序规则不同 | 看两表的 CHARSET / COLLATE |
| 引擎不是 InnoDB | MyISAM 不支持外键 |

**建完必须验一遍**：

```sql
SHOW TABLES;                    -- 应该有 4 张
DESC orders;                    -- 看约束在不在
SHOW CREATE TABLE orders\G      -- 看完整定义（外键名、字符集、引擎）
```

## 三、测试数据

### 3.1 插入语句

- INSERT INTO 表名 (列1, 列2,列3) VALUES (值1, 值2,值3);

```
INSERT INTO users (username, phone, status) VALUES
('张三丰', '13800000001', 1),
('李四',   '13800000002', 1),
('王五',   '13800000003', 0),
('张三丰', '13800000004', 1),
('赵六',   '13800000005', 1);
```

表内数据之间需要用英文逗号分开

**插入的五条规矩**：

1. **不要手写 `id`**（交给 `AUTO_INCREMENT`）
2. 字段顺序和 `VALUES` 顺序必须一一对应
3. 字符串用 `'单引号'`
4. 多行插入用一条 `INSERT`，比 10 条快
5. **故意造脏数据** —— 这才叫“测试数据”

```sql
INSERT INTO users (username, phone, status) VALUES
('张三丰', '13800000001', 1),
('李四',   '13800000002', 1);
```

### 3.2 我故意造的脏数据（逐条说明：为什么造它、它对应哪个 Bug 类型）

- 用户：张三丰和"张三丰"重名，手机号不同，检查重名

```
INSERT INTO users (username, phone, status) VALUES
('张三丰', '13800000001', 1),
('李四',   '13800000002', 1),
('王五',   '13800000003', 0),
('张三丰', '13800000004', 1),
('赵六',   '13800000005', 1);
```

- 商品：最后一个库存是负数，脏数据

```
INSERT INTO products (name, price, stock) VALUES
('机械键盘',   299.00, 100),
('无线鼠标',    99.00, 200),
('显示器',    1299.00,  30),
('USB 数据线',  19.90, 500),
('笔记本支架',  89.00,  50),
('坏数据商品',  50.00,  -5);
```

- 订单：第一、二、七条金额对不上，第八条没有明细

```
INSERT INTO orders (user_id, total_amount, status) VALUES
(1,  398.00, 1),
(1,   99.00, 1),
(2, 1299.00, 0),
(3,  299.00, 2),
(2,  108.90, 1),
(4,   50.00, 0),
(1,  999.00, 1),
(5,    0.00, 0),
(1,  199.00, 1),
(2,   19.90, 1);
```

- 订单明细

```
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
(1, 1, 1, 299.00),
(1, 2, 1,  99.00),
(2, 2, 1,  99.00),
(3, 3, 1, 1299.00),
(4, 1, 1, 299.00),
(5, 4, 1,  19.90),
(5, 5, 1,  89.00),
(6, 6, 1,  50.00),
(7, 4, 1,  19.90),
(7, 5, 1,  70.00),
(9, 2, 1,  99.00),
(9, 1, 1, 100.00),
(10, 4, 1, 19.90),
(1, 4, 1, 19.90),
(2, 5, 1, 89.00);
```

**判断表内数据数量**

```
SELECT 'users' AS t, COUNT(*) FROM users
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'orders', COUNT(*) FROM orders
UNION ALL SELECT 'order_items', COUNT(*) FROM order_items;
```

**结果**

```
+-------------+----------+
| t           | COUNT(*) |
+-------------+----------+
| users       |        5 |
| products    |        6 |
| orders      |       10 |
| order_items |       15 |
+-------------+----------+
```


### 3.3 为什么需要 SET FOREIGN_KEY_CHECKS = 0

- 真实测试环境里，脏数据往往违反了约束但依然存在（历史原因、脚本 bug）。要模拟它，得临时绕过外键

```
SET FOREIGN_KEY_CHECKS = 0;      -- 临时关闭外键检查

-- 插一条指向不存在订单的明细（order_id=999）
INSERT INTO order_items (order_id, product_id, quantity, unit_price)
VALUES (999, 1, 1, 299.00);

SET FOREIGN_KEY_CHECKS = 1;      -- 一定要恢复！
```

插完孤儿明细，再数一次：

```sql
SELECT COUNT(*) FROM order_items;    -- 16
```

## 四、单表查询

### 4.1 SELECT 基本形

```
SELECT 列1, 列2        -- 要什么
FROM 表                 -- 从哪来
WHERE 条件              -- 过滤哪些行
ORDER BY 列 DESC        -- 怎么排
LIMIT 10;               -- 要几条
SELECT * FROM users;             -- 全部（练习可以，生产别用）
SELECT username, phone FROM users;            -- 指定列
SELECT username AS 用户名, phone AS 手机号 FROM users;   -- 别名（中文要加引号才安全）
SELECT DISTINCT username FROM users;          -- 去重
```

### 4.2 WHERE 运算符表

| 类 | 写法 | 例子 |
| --- | --- | --- |
| 比较 | = != <> > < >= <= | price > 100 |
| 区间 | BETWEEN a AND b（含两端） | price BETWEEN 50 AND 300 |
| 列表 | IN (...) / NOT IN (...) | status IN (0,1) |
| 模糊 | LIKE '张%' / LIKE '%鼠标%' / LIKE '_三丰' | % 任意多个字符，_ 一个字符 |
| 空值 | IS NULL / IS NOT NULL | 不能用 = NULL |
| 逻辑 | AND / OR / NOT | 注意优先级：AND 高于 OR，混用时加括号 |
| 空安全比较 | <=> | a <=> NULL 可以判空 |

### 4.3 NULL 的三个陷阱 + 我实际跑的结果

#### 永远判空：

**错误输入：**

```
SELECT * FROM users WHERE phone = NULL;
```

**错误输入导致的输出：**

```
Empty set
```

**正确输入：**

```
SELECT * FROM users WHERE phone IS NULL;
```

**正确输出：**

```
Empty set (0.00 sec)
```

- 正确输出的空集是因为users库规定了phone非空。错误输出空集是因为无论比较的是什么都输出空集

#### 运算符遇到 NULL 

**错误输入：**

```
SELECT NULL = NULL;
```

**错误输入导致的输出：**

```
 NULL 
```

**正确输入：**

```
SELECT NULL <=> NULL;
```

**正确输出：**

```
1
```

- = NULL会把结果变成NULL，<=> NULL会把NULL当成普通值比较

#### 前者数行数，后者跳过 NULL

**输入：**

```
SELECT COUNT(*), COUNT(phone) FROM users;
```

**输出：**

```
| COUNT(*) | COUNT(phone) |
+----------+--------------+
|        5 |            5 
```

- “相等是因为 phone 是 NOT NULL，没有 NULL 可跳过；换成可空的 email 列才会出现 5 vs 4”

### 4.4 书写顺序 vs 执行顺序（画一遍）

- 写的顺序

```mermaid
flowchart LR
    A[SELECT ] --> B[FROM ]
    B --> C[WHERE ]
    C --> D[GROUP BY]
    D --> E[HAVING ]
    E --> F[ORDER BY]
    F --> G[LIMIT]
```

- 实际执行的顺序

```mermaid
flowchart LR
    A[FROM] --> B[WHERE]
    B --> C[GROUP BY]
    C --> D[HAVING]
    D --> E[SELECT]
    E --> F[ORDER BY]
    F --> G[LIMIT]
```

#### 结论

1. WHERE 里不能用聚合函数 —— 因为 WHERE 执行时还没分组，COUNT() 还不存在
2. HAVING 里可以用聚合函数 —— 它在分组之后
3. ORDER BY 可以用 SELECT 里起的别名 —— 因为 SELECT 已经算完了

### 4.5 聚合与 GROUP BY / HAVING

| 函数 | 作用 | 注意 |
| --- | --- | --- |
| COUNT(*) | 行数 | 包含 NULL 行 |
| COUNT(列) | 该列非 NULL 的行数 | 有 NULL 时比 COUNT(*) 小 |
| COUNT(DISTINCT 列) | 该列不同值的个数 | 去重计数 |
| SUM / AVG | 求和 / 平均 | AVG 会忽略 NULL，分母是"非 NULL 行数" |
| MAX / MIN | 最值 | 字符串也能比较 |

#### ONLY_FULL_GROUP_BY（MySQL 5.7 起默认开启）

**规则**：`SELECT` 里的列，**要么出现在 `GROUP BY` 里，要么被聚合函数包住**。

```sql
-- ❌ 报错
SELECT username, COUNT(*) FROM users GROUP BY status;
```

```
ERROR 1055 (42000): Expression #1 of SELECT list is not in GROUP BY clause
and contains nonaggregated column 'qa_practice.users.username'
which is not functionally dependent on columns in GROUP BY clause
```

**为什么报错**：`status=1` 那一组里有 4 行、3 个 `username`，MySQL 不知道该返回哪个 —— 与其给你一个随机的，不如直接报错。

**三种改法**：

```sql
-- ① 把列也放进 GROUP BY（按更细的维度分组）
SELECT status, username, COUNT(*) FROM users GROUP BY status, username;

-- ② 用聚合函数包住（明确"我要这一组里最大的那个"）
SELECT status, MAX(username) AS 任一用户名, COUNT(*) FROM users GROUP BY status;

-- ③ 用 ANY_VALUE 明确表示"随便取一个"（MySQL 5.7.5+）
SELECT status, ANY_VALUE(username) AS 任一用户名, COUNT(*) FROM users GROUP BY status;
```

**例外：函数依赖**

按**主键**分组时，同表的其它列可以直接 SELECT（因为主键能唯一确定一行）：

```sql
SELECT o.id, o.total_amount, SUM(i.quantity * i.unit_price)
FROM orders o JOIN order_items i ON i.order_id = o.id
GROUP BY o.id, o.total_amount;    -- 只写 GROUP BY o.id 也能过
```

**怎么查 / 怎么临时关**：

```sql
SELECT @@sql_mode;    -- 看是否包含 ONLY_FULL_GROUP_BY

-- 只关当前会话（练习环境才这么做，正式环境别关）
SET SESSION sql_mode = REPLACE(@@sql_mode, 'ONLY_FULL_GROUP_BY', '');
```

> **测试视角**：这个报错其实在保护你。
> 关掉之后，`SELECT username, COUNT(*) ... GROUP BY status` 会返回**组里随机一行的 username** ——
> 同一条 SQL 两次执行结果可能不同，是典型的"偶发失败"来源。**宁可报错，不要随机。**

### 4.6 20 条查询（问题 → SQL → 结果，逐条）

| # | 业务问题 | 覆盖知识点 |
| --- | --- | --- |
| 1 | 查出所有用户 | 基础 SELECT |
| 2 | 只查用户名和手机号 | 指定列 |
| 3 | 用户名统一显示为「昵称」列 | 列别名 |
| 4 | 列出所有不重复的用户名 | DISTINCT |
| 5 | 查状态为正常的用户 | WHERE + 数值 |
| 6 | 查被禁用的用户 | WHERE |
| 7 | 查价格大于 100 的商品 | 比较运算 |
| 8 | 查价格在 50 到 300 之间的商品 | BETWEEN |
| 9 | 查状态是「待支付」或「已取消」的订单 | IN |
| 10 | 查名字里带「键盘」的商品 | LIKE |
| 11 | 查用户名以「张」开头的用户 | LIKE 前缀 |
| 12 | 查手机号倒数第 2 位是 3 的用户 | LIKE _ 通配 |
| 13 | 商品按价格从高到低排，价格相同按 id 升序 | ORDER BY 多列 |
| 14 | 取价格最高的 3 个商品 | ORDER BY + LIMIT |
| 15 | 统计用户总数 | COUNT(*) |
| 16 | 统计有手机号的用户数（假设以后可能有空） | COUNT(列) |
| 17 | 按订单状态分组，统计每种状态的单数和总金额 | GROUP BY + 聚合 |
| 18 | 只统计总金额大于 500 的订单状态 | HAVING |
| 19 | 查每个用户有多少个订单，按下单数降序 | GROUP BY + ORDER BY |
| 20 | 查订单金额的最大值、最小值、平均值 | MAX / MIN / AVG |

**#1 SQL**

```
SELECT * FROM users;
```

**#1 结果**

```
+----+----------+-------------+--------+---------------------+
| id | username | phone       | status | created_at          |
+----+----------+-------------+--------+---------------------+
|  1 | 张三丰   | 13800000001 |      1 | 2026-10-29 15:37:45 |
|  2 | 李四     | 13800000002 |      1 | 2026-10-29 15:37:45 |
|  3 | 王五     | 13800000003 |      0 | 2026-10-29 15:37:45 |
|  4 | 张三丰   | 13800000004 |      1 | 2026-10-29 15:37:45 |
|  5 | 赵六     | 13800000005 |      1 | 2026-10-29 15:37:45 |
+----+----------+-------------+--------+---------------------+
```

**#2 SQL**

```
SELECT username,phone FROM users;
```

**#2 结果**

```
+----------+-------------+
| username | phone       |
+----------+-------------+
| 张三丰   | 13800000001 |
| 李四     | 13800000002 |
| 王五     | 13800000003 |
| 张三丰   | 13800000004 |
| 赵六     | 13800000005 |
+----------+-------------+
```

**#3 SQL**

```
SELECT username AS "昵称" FROM users; 
```

**#3 结果**

```
+--------+
| 昵称   |
+--------+
| 张三丰 |
| 李四   |
| 王五   |
| 张三丰 |
| 赵六   |
+--------+
```

**#4 SQL**

```
SELECT DISTINCT username FROM users;
```

**#4 结果**

```
+----------+
| username |
+----------+
| 张三丰   |
| 李四     |
| 王五     |
| 赵六     |
+----------+
```

**#5 SQL**

```
SELECT username FROM users WHERE status = 1;
```

**#5 结果**

```
+----------+
| username |
+----------+
| 张三丰   |
| 李四     |
| 张三丰   |
| 赵六     |
+----------+
```

**#6 SQL**

```
SELECT username FROM users WHERE status = 0;
```

**#6 结果**

```
+----------+
| username |
+----------+
| 王五     |
+----------+
```

**#7 SQL**

```
SELECT name FROM products WHERE price > 100;
```

**#7 结果**

```
+----------+
| name     |
+----------+
| 机械键盘 |
| 显示器   |
+----------+
```

**#8 SQL**

```
SELECT name FROM products WHERE price BETWEEN 50 AND 300;
```

**#8 结果**

```
+------------+
| name       |
+------------+
| 机械键盘   |
| 无线鼠标   |
| 笔记本支架 |
| 坏数据商品 |
+------------+
```

**#9 SQL**

```
SELECT * FROM orders WHERE status IN (0,2);
```

**#9 结果**

```
+----+---------+--------------+--------+---------------------+
| id | user_id | total_amount | status | created_at          |
+----+---------+--------------+--------+---------------------+
|  3 |       2 |      1299.00 |      0 | 2026-10-29 15:51:30 |
|  4 |       3 |       299.00 |      2 | 2026-10-29 15:51:30 |
|  6 |       4 |        50.00 |      0 | 2026-10-29 15:51:30 |
|  8 |       5 |         0.00 |      0 | 2026-10-29 15:51:30 |
+----+---------+--------------+--------+---------------------+
```

**#10 SQL**

```
SELECT * FROM products WHERE name LIKE '%键盘%';
```

**#10 结果**

```
+----+----------+--------+-------+---------------------+
| id | name     | price  | stock | created_at          |
+----+----------+--------+-------+---------------------+
|  1 | 机械键盘 | 299.00 |   100 | 2026-10-29 15:48:38 |
+----+----------+--------+-------+---------------------+
```

**#11 SQL**

```
SELECT * FROM users WHERE username LIKE '张%';
```

**#11 结果**

```
+----+----------+-------------+--------+---------------------+
| id | username | phone       | status | created_at          |
+----+----------+-------------+--------+---------------------+
|  1 | 张三丰   | 13800000001 |      1 | 2026-10-29 15:37:45 |
|  4 | 张三丰   | 13800000004 |      1 | 2026-10-29 15:37:45 |
+----+----------+-------------+--------+---------------------+
```

**#12 SQL**

```
SELECT * FROM users WHERE phone LIKE '%3_';
```

**#12 结果**

```
Empty set (0.00 sec)
```

- _ 恰好匹配一个字符，'%3_' = 倒数第二位是 3；我造的手机号倒数第二位都是 0，所以查不到是正确结果，不是语法错

**#13 SQL**

```
SELECT * FROM products ORDER BY price DESC, id ASC;
```

**#13 结果**

```
+----+------------+---------+-------+---------------------+
| id | name       | price   | stock | created_at          |
+----+------------+---------+-------+---------------------+
|  3 | 显示器     | 1299.00 |    30 | 2026-10-29 15:48:38 |
|  1 | 机械键盘   |  299.00 |   100 | 2026-10-29 15:48:38 |
|  2 | 无线鼠标   |   99.00 |   200 | 2026-10-29 15:48:38 |
|  5 | 笔记本支架 |   89.00 |    50 | 2026-10-29 15:48:38 |
|  6 | 坏数据商品 |   50.00 |    -5 | 2026-10-29 15:48:38 |
|  4 | USB 数据线 |   19.90 |   500 | 2026-10-29 15:48:38 |
+----+------------+---------+-------+---------------------+
```

**#14 SQL**

```
SELECT * FROM products ORDER BY price DESC LIMIT 3;
```

**#14 结果**

```
+----+----------+---------+-------+---------------------+
| id | name     | price   | stock | created_at          |
+----+----------+---------+-------+---------------------+
|  3 | 显示器   | 1299.00 |    30 | 2026-10-29 15:48:38 |
|  1 | 机械键盘 |  299.00 |   100 | 2026-10-29 15:48:38 |
|  2 | 无线鼠标 |   99.00 |   200 | 2026-10-29 15:48:38 |
+----+----------+---------+-------+---------------------+
```

**#15 SQL**

```
SELECT COUNT(*) AS 用户总数 FROM users;
```

**#15 结果**

```
+----------+
| 用户总数 |
+----------+
|        5 |
+----------+
```

**#16 SQL**

```
SELECT COUNT(phone) AS 用户数 FROM users;
```

**#16 结果**

```
+--------+
| 用户数 |
+--------+
|      5 |
+--------+
```

**#17 SQL**

```
SELECT status, COUNT(*) AS 单数, SUM(total_amount) AS 总额
FROM orders GROUP BY status ORDER BY status;
```

**#17 结果**

```
+--------+------+---------+
| status | 单数 | 总额    |
+--------+------+---------+
|      0 |    3 | 1349.00 |
|      1 |    6 | 1823.80 |
|      2 |    1 |  299.00 |
+--------+------+---------+
```

**#18 SQL**

```
SELECT status, SUM(total_amount) AS 总额
FROM orders GROUP BY status HAVING SUM(total_amount) > 500
ORDER BY status;
```

**#18 结果**

```
+--------+---------+
| status | 总额    |
+--------+---------+
|      0 | 1349.00 |
|      1 | 1823.80 |
+--------+---------+
```

> 不写 `ORDER BY` 时，行序**不保证**。这次碰巧是 1 在前，复跑可能就变了 ——
> 用例里要断言顺序，必须显式排序，否则就是偶发失败。

**#19 SQL**

```
SELECT user_id, COUNT(*) AS 下单数
FROM orders GROUP BY user_id ORDER BY 下单数 DESC;
```

**#19 结果**

```
+---------+--------+
| user_id | 下单数 |
+---------+--------+
|       1 |      4 |
|       2 |      3 |
|       3 |      1 |
|       4 |      1 |
|       5 |      1 |
+---------+--------+
```

**#20 SQL**

```
SELECT MAX(total_amount), MIN(total_amount), AVG(total_amount) FROM orders;
```

**#20 结果**

```
+-------------------+-------------------+-------------------+
| MAX(total_amount) | MIN(total_amount) | AVG(total_amount) |
+-------------------+-------------------+-------------------+
|           1299.00 |              0.00 |        347.180000 |
+-------------------+-------------------+-------------------+
```

## 五、改与删

### 5.1 三条铁律

1. 改之前先 SELECT 验证条件命中哪些行

```
SELECT * FROM orders WHERE status = 2;
```

2. 用事务包一层，错了能回滚

```
START TRANSACTION;
UPDATE orders SET status = 1 WHERE status = 2;
SELECT * FROM orders WHERE status = 2;   -- 确认影响行数对不对
-- ROLLBACK;    ← 后悔就回滚
COMMIT;         ← 确认无误再提交
```

3. 一次只改一类东西

```
UPDATE products SET stock = stock - 1 WHERE id = 1;
```

### 5.2 忘写 WHERE 的后果（实际影响行数）

```
UPDATE orders SET status = 2;    -- ⚠️ 全表 10 行状态全变 2
DELETE FROM orders;              -- ⚠️ 全表清空
```

- MySQL 命令行会提示 `Rows matched: 10  Changed: 9  Warnings: 0` ——
  **`matched` 是"命中几行"，`changed` 才是"真正改了几行"**。
  这次订单 4 本来就是 `status=2`，所以命中 10 行、实际只改了 9 行。
  看这两个数，就知道自己有没有改多。
- SET SQL_SAFE_UPDATES = 1;事前防范
- `SET SQL_SAFE_UPDATES = 1;` 开了之后，**没写 `WHERE`、或 `WHERE` 里没用索引列的 `UPDATE`/`DELETE` 会被直接拒绝执行**。
Navicat 里对应「工具 → 选项 → 安全更新」那个开关。

### 5.3 DELETE / TRUNCATE / DROP 对比

| | 删什么 | 能回滚吗 | 自增 id | 速度 | 典型用途 |
| --- | --- | --- | --- | --- | --- |
| DELETE FROM t WHERE ... | 符合条件的行  |✅ 可以（事务内） | 不重置 | 慢（逐行） | 日常清理 |
| TRUNCATE TABLE t | 全部行 | ❌ 不可以 | 重置为 1 | 快 | 清空测试数据 |
| DROP TABLE t | 表 + 数据 | ❌ 不可以 | —— | 最快 | 删表重建 |

### 5.4 事务回滚实验的实际输出（回滚前后行数）

**开始前**

```
+----+---------+--------------+--------+---------------------+
| id | user_id | total_amount | status | created_at          |
+----+---------+--------------+--------+---------------------+
|  4 |       3 |       299.00 |      2 | 2026-10-29 15:51:30 |
+----+---------+--------------+--------+---------------------+
```

**回滚前**

```
Empty set (0.00 sec)
```

**回滚后**

```
+----+---------+--------------+--------+---------------------+
| id | user_id | total_amount | status | created_at          |
+----+---------+--------------+--------+---------------------+
|  4 |       3 |       299.00 |      2 | 2026-10-29 15:51:30 |
+----+---------+--------------+--------+---------------------+
```

```
START TRANSACTION;
DELETE FROM order_items;      -- 删光
ROLLBACK;                     -- ✅ 能救回
SELECT COUNT(*) FROM order_items;   -- 还是 16

TRUNCATE TABLE order_items;   -- 删光
ROLLBACK;                     -- ❌ 救不回（DDL 隐式提交）
SELECT COUNT(*) FROM order_items;   -- 0
```

**再验证一个"救不回来"的**：

```sql
TRUNCATE TABLE order_items;        -- ⚠️ DDL，隐式提交
SELECT COUNT(*) FROM order_items;  -- 0
ROLLBACK;                          -- 无效
SELECT COUNT(*) FROM order_items;  -- 还是 0
```

结论：`DELETE` 在事务里能回滚，`TRUNCATE` 不能 —— 这就是“改数据前先 `START TRANSACTION`”的理由。

## 六、脏数据体检查询

### 6.1 金额对不上

> ⚠️ 注意：`JOIN` 是内连接，**只保留两边都有的行**。订单 8 没有明细，所以**根本不在上面结果里** ——
> 想查它必须用 6.2 的 `LEFT JOIN`。这也是为什么对账要同时跑两条查询。

**输入**

```
SELECT o.id,
       o.total_amount                AS 订单金额,
       SUM(i.quantity * i.unit_price) AS 明细合计
FROM orders o
JOIN order_items i ON i.order_id = o.id
GROUP BY o.id, o.total_amount
HAVING o.total_amount <> SUM(i.quantity * i.unit_price);
```

**输出**

```
+----+----------+----------+
| id | 订单金额 | 明细合计 |
+----+----------+----------+
|  1 |   398.00 |   417.90 |
|  2 |    99.00 |   188.00 |
|  7 |   999.00 |    89.90 |
+----+----------+----------+
```

**差异**

| 订单 | 差异方向 | 可能的原因 |
| --- | --- | --- |
| 1、2 | 明细合计 > 账面 | 下单时漏把某条明细计入总额（金额少算） |
| 7 | 明细合计 < 账面 | 账面虚高（多收用户钱 / 数据被改过） |

- 内连接 = **只保留 `ON` 条件匹配上**的行；订单 8 没有明细、匹配不上，所以查不到 ——
  它要靠 6.2 的 `LEFT JOIN` 才出得来

### 6.2 空单

**输入**

```
SELECT o.id, o.total_amount
FROM orders o
LEFT JOIN order_items i ON i.order_id = o.id
WHERE i.id IS NULL;
```

**输出**

```
+----+--------------+
| id | total_amount |
+----+--------------+
|  8 |         0.00 |
+----+--------------+
```

### 6.3 孤儿明细

**输入**

```
SELECT i.*
FROM order_items i
LEFT JOIN orders o ON o.id = i.order_id
WHERE o.id IS NULL;
```

**输出**

```
+----+----------+------------+----------+------------+
| id | order_id | product_id | quantity | unit_price |
+----+----------+------------+----------+------------+
| 16 |      999 |          1 |        1 |     299.00 |
+----+----------+------------+----------+------------+
```

### 6.4 负库存

**输入**

```
SELECT * FROM products WHERE stock < 0;
SELECT * FROM orders    WHERE total_amount < 0;
SELECT * FROM order_items WHERE quantity <= 0 OR unit_price <= 0;
```

**输出**

```
+----+------------+-------+-------+---------------------+
| id | name       | price | stock | created_at          |
+----+------------+-------+-------+---------------------+
|  6 | 坏数据商品 | 50.00 |    -5 | 2026-10-29 15:48:38 |
+----+------------+-------+-------+---------------------+

Empty set (0.00 sec)

Empty set (0.00 sec)

```

### 6.5 重名用户

**输入**

```
SELECT username, COUNT(*) AS 同名数
FROM users GROUP BY username HAVING COUNT(*) > 1;
```

**输出**

```
+----------+--------+
| username | 同名数 |
+----------+--------+
| 张三丰   |      2 |
+----------+--------+
```

### 6.6 我的结论（先分清两层）

**第一层：工具层 —— 我的 SQL 能不能命中这类异常**

| 类别 | 查询 | 命中数据 | 能否命中 |
| --- | --- | --- | --- |
| 缺（无明细订单） | 6.2 | 订单 8 | ✅ |
| 多（重名用户） | 6.3 | 张三丰 ×2 | ✅ |
| 错（金额对不上） | 6.1 | 订单 1、2、7 | ✅ |
| 孤（孤儿明细） | 6.4 | order_id = 999 | ✅ |
| 矛盾（已取消却有明细） | 6.5 | 订单 4 | ✅ |

**第二层：业务层 —— 假设这是线上真实数据，我会怎么判**

> ⚠️ 上面这些数据**全部是我自己 INSERT 造的**，不是系统产生的。
> 所以这一层不是"宣布它是 Bug"，而是"如果真实发生，我依据什么判断"。

| 类别 | 我的判定 | 依据 / 还需要问什么 |
| --- | --- | --- |
| 负库存 | **大概率 Bug**，前提是先确认是否允许超卖 | 允许超卖的业务，负库存是设计而不是缺陷 |
| 金额不符 | **Bug**，但要按方向分级 | 明细>账面 = 少收钱；账面>明细 = 多收钱 |
| 孤儿明细 | **Bug（最严重）** | 且能推出：这张表没有外键，或有人关过 FOREIGN_KEY_CHECKS |
| 重名用户 | **取决于登录方式** | 用户名登录 → 必须加 UNIQUE；手机号登录 → 无影响 |
| 空单 | **待确认** | 允许"先建单后加商品"就正常；还要问有没有超时取消 |
| 已取消却有明细 | **Bug** | 取消时应作废明细，否则 GMV 统计会把已取消的算进去 |

**判"是不是 Bug"之前必须先问三件事**：

1. 这批数据的**产生路径**是什么？（系统自动 / 人工后台 / 数据迁移）
2. **需求**怎么定义？（允许超卖吗？允许重名吗？允许空单吗？）
3. 异常的**方向**是什么？（少算还是多算、缺还是多）

## 七、还没搞懂的

- 其中的SUM(total_amount)和GROUP BY status ORDER BY status是什么作用？

```
你写的：  SELECT → FROM → WHERE → GROUP BY → HAVING → ORDER BY → LIMIT
实际跑的：FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT
                    ↑              ↑                  ↑
                 先过滤行        先分桶            最后才排序
```

- 为什么不能是SELECT status, SUM(total_amount) AS 总额
FROM orders SUM(total_amount) > 500;

```
WHERE 过滤行（分组前），HAVING 过滤组（分组后）。 条件里用到了聚合函数（SUM/COUNT/AVG），就只能用 HAVING —— 因为那时才有这些值。 而 FROM 表 表达式 这种写法不存在：条件必须挂在子句关键字后面。
```
