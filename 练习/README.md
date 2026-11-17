# 加练（每天 15 分钟，可选）

> **目的**：Shell / SQL / 断言 都是"手写型"技能 —— 看懂不算会，**写出来才算**。

## 规则

| 项 | 规则 |
|---|---|
| **时长** | **15 分钟硬上限**，到点就停 |
| **方式** | **合上笔记**，写完再对照 |
| **频率** | 每天**一项**（不是三项全做），轮换 |
| **达标线** | **一周做够 4 次**就算合格，不用 7 天 |
| **跳过条件** | 主线没做完 / 已卡 3 小时以上 → **直接跳过，不欠账** |

**判据**：

> **15 分钟结束时，手里必须有一个"能跑的东西"** —— 不是"看了几个知识点"。
> **加练是加固，不是加课。** 它让你多干 20 分钟却让第二天起不来，就是负收益。

## 记录在哪

| 内容 | 位置 |
|---|---|
| 练习文件 | `练习/<技能>/日期-主题.<扩展名>` |
| 卡点 | 当天笔记末尾一行：`- 加练：Shell 磁盘告警，卡在 awk 取第 5 列` |
| 进度 | 下面的「进度表」 |

**别把完整代码塞进每天笔记** —— 笔记已经 200 行，再塞练习会变垃圾场。

## 进度表

| 日期 | 技能 | 题目 | 状态 | 卡在哪 |
|---|---|---|---|---|
| 11/16 | Shell | 磁盘空间告警 | ⬜ | |
| 11/17 | SQL | 订单数 ≥ 2 的用户 | ⬜ | |
| 11/18 | 断言 | 给 `08-模拟 500` 补三层断言 | ⬜ | |
| 11/19 | Shell | 日志状态码统计 | ⬜ | |
| 11/20 | SQL | 查出"有订单无明细"的脏数据 | ⬜ | |
| 11/21 | 断言 | 同一条断言，三种写法 | ⬜ | |

> 状态：⬜ 未做 / 🔁 做过但卡 / ✅ 写完且能跑

---

## 题目

### 11/16（周一）· Shell：磁盘空间告警

**题面**：写 `练习/shell/2026-11-16-磁盘告警.sh`

1. 用 `df -h` 取**根分区**使用率
2. 超过 `80%` 打印 `WARN: 磁盘使用率 8x%`，否则 `OK: 8x%`
3. WARN 时 `exit 1`

**考点**：`df` / `awk` 取列 / `gsub` 去 `%` / `[ ]` 比较 / `exit` 码

**卡住了看这个**：

```bash
df -h / | awk 'NR==2 {print $5}'
```

**参考实现**（写完再看）：

```bash
#!/usr/bin/env bash
usage=$(df -h / | awk 'NR==2 {gsub(/%/,"",$5); print $5}')
if [ "$usage" -gt 80 ]; then
    echo "WARN: 磁盘使用率 ${usage}%"
    exit 1
fi
echo "OK: ${usage}%"
```

---

### 11/17（周二）· SQL：订单数 ≥ 2 的用户

**题面**：在 `qa_practice` 库里查

> 查出**下单次数 ≥ 2** 的用户的 `id`、`username`、订单数，按订单数降序。

**表结构**（`qa_practice` 库，Day 12 建过）：

| 表 | 字段 |
|---|---|
| `users` | `id`、`username`（以 `DESC users` 为准） |
| `orders` | `id`、`user_id`（→ users.id）、`total_amount`、`status`、`created_at` |

**不记得字段名就先查**：

```sql
USE qa_practice;
SHOW TABLES;
DESC users;
DESC orders;
```

**两步验证法**（比“写完看结果”可靠）：

```sql
-- ① 先看分布，不筛选
SELECT user_id, COUNT(*) AS cnt
FROM orders
GROUP BY user_id
ORDER BY cnt DESC;

-- ② 数出“有几个 user_id 的 cnt >= 2” → 这就是期望条数
-- ③ 再写筛选版，对一下条数
```

**考点**：`JOIN` + `GROUP BY` + `HAVING` + `ORDER BY`

**判据**：15 分钟内写出，且**结果条数能对上**（先自己数一遍期望值）。

**卡住了想三件事**：

1. 计数用 `COUNT(*)` 还是 `COUNT(o.id)`？**后者才对**（左连接时 NULL 不计数）
2. 过滤"聚合后的条件"用 `WHERE` 还是 `HAVING`？
3. `GROUP BY` 要带哪些列？

**参考实现**（写完再看）：

```sql
SELECT u.id, u.name, COUNT(o.id) AS order_cnt
FROM users u
JOIN orders o ON o.user_id = u.id
GROUP BY u.id, u.name
HAVING COUNT(o.id) >= 2
ORDER BY order_cnt DESC;
```

---

### 11/18（周三）· 断言：给 `08-模拟 500` 补三层

**题面**：打开 Postman 的 `08-模拟 500`，把断言从"只判状态码"改成**三层**：

| 层 | 断言什么 |
|---|---|
| L1 协议 | 状态码是 500 |
| L2 数据 | 响应体为空 |
| L3 安全 | 响应里**不含** `Traceback` / `SQL` / `/home/` / `password` 任一关键词 |

**考点**：`pm.response.text()` 子串检查（Day 17 学过，别用 `json()`）

**判据**：三条断言名都能让外行看懂"在验什么"。

**卡住了想**：L3 为什么不用 `json()`？

**参考实现**（写完再看）：

```js
pm.test("状态码是 500", function () {
    pm.response.to.have.status(500);
});

pm.test("错误响应没有 body", function () {
    pm.expect(pm.response.text()).to.be.empty;
});

pm.test("5xx 不泄露堆栈或内网路径", function () {
    const t = pm.response.text().toLowerCase();
    ["traceback", "sql", "/home/", "password"].forEach(function (kw) {
        pm.expect(t, "泄露了 " + kw).to.not.include(kw);
    });
});
```

---

### 11/19（周四）· Shell：日志状态码统计

**题面**：写 `练习/shell/2026-11-19-日志状态码.sh`

> 从 `access.log` 里统计**每个 HTTP 状态码出现的次数**，按次数降序打印：
> `200 1523`

**先造一个测试日志**（别用真日志）：

```bash
cd 练习/shell
printf '%s
'  '1.1.1.1 - - [16/Nov/2026] "GET /a HTTP/1.1" 200 123'  '2.2.2.2 - - [16/Nov/2026] "GET /b HTTP/1.1" 404 0'  '3.3.3.3 - - [16/Nov/2026] "POST /c HTTP/1.1" 200 456'  '4.4.4.4 - - [16/Nov/2026] "GET /d HTTP/1.1" 500 12'  '5.5.5.5 - - [16/Nov/2026] "GET /e HTTP/1.1" 200 78'  > access.log
```

**考点**：`awk` 取字段 + `sort` + `uniq -c` + `sort -rn`

**判据**：`200` 应该出现 3 次、`404` 和 `500` 各 1 次。

**卡住了看这个**：

```bash
awk '{print $9}' access.log
```

**参考实现**（写完再看）：

```bash
awk '{print $9}' access.log | sort | uniq -c | sort -rn
```

---

### 11/20（周五）· SQL：查出"有订单无明细"的脏数据

**题面**：在 `qa_practice` 库里查

> 查出**有订单、但 `order_items` 里没有对应明细**的订单 `id` 和金额。

**背景**：你 Day 12 做过"五类脏数据"，这是其中一类 —— **孤儿数据**。

**考点**：`LEFT JOIN` + `IS NULL`

**判据**：能解释"为什么 `LEFT JOIN ... WHERE 右表.id IS NULL` 能找出孤儿"。

**卡住了想**：`INNER JOIN` 能不能找出"没有匹配"的行？

**参考实现**（写完再看）：

```sql
SELECT o.id, o.total_amount
FROM orders o
LEFT JOIN order_items oi ON oi.order_id = o.id
WHERE oi.id IS NULL;
```

---

### 11/21（周六）· 断言：同一条断言，三种写法

**题面**：打开 `02-测试 GET 带 token`，用**三种不同方式**写同一个断言（"响应里有 authenticated 且为 true"）：

1. `pm.expect(...)` 直接比较
2. `pm.response.to.have.jsonBody(...)`
3. `pm.response.to.have.jsonSchema(...)`

**考点**：三种写法的**适用场景不同** ——

| 写法 | 什么时候用 |
|---|---|
| `pm.expect` | 要**精确控制**错误信息、要比大小/包含 |
| `have.jsonBody` | 只看"某个字段等于某个值"，最快 |
| `jsonSchema` | 校验**整个结构**（字段类型、必填） |

**判据**：能说出"为什么同一个断言要会三种写法"。

**参考实现**（写完再看）：

```js
pm.test("① expect：authenticated 为 true", function () {
    pm.expect(pm.response.json().authenticated).to.eql(true);
});

pm.test("② jsonBody：字段值匹配", function () {
    pm.response.to.have.jsonBody("authenticated", true);
});

pm.test("③ schema：结构符合", function () {
    pm.response.to.have.jsonSchema({
        type: "object",
        required: ["authenticated"],
        properties: { authenticated: { type: "boolean" } }
    });
});
```

---

## 每周日复盘时

**扫一眼进度表**，回答两个问题：

1. **哪项练得最少？**（大概率是"最不想练"的那项 —— 那才是短板）
2. **哪条一直 🔁？**（说明 15 分钟不够，或者题目超纲）

**然后调整下周的题目难度 —— 别让加练变成"每天重复会的"。**
