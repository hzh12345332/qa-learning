# Day 27 ｜ 生成器 / 迭代器 / 推导式

产出：

| 文件 | 内容 |
|---|---|
| `01-生成器迭代器笔记.md` | 笔记主体（340 行，七章） |
| `scripts/01_iterator.py` | 手写迭代器 `CountDown`：`__iter__` + `__next__` |
| `scripts/02_iterator_once.py` | 迭代器只能遍历一次（第二次 `[]`） |
| `scripts/03_generator.py` | 生成器：`yield` 暂停/恢复、`counter`、`close` 触发 `finally` |
| `scripts/04_comprehension.py` | 四种推导式 + 两种 `if` 位置 + `getsizeof` 对比 |
| `scripts/05_pipeline.py` | 生成器管道（读 → 筛 → 变形），惰性求值 |
| `练习/sql/2026-11-20-孤儿数据.sql` | 加练：`LEFT JOIN ... IS NULL` 找孤儿订单 |

## 今天搞清的七点

1. **`for x in obj` 只是语法糖**：`iter(obj)` 拿迭代器 → 反复 `next()` → `StopIteration` 结束。
   **可迭代对象有 `__iter__`；迭代器额外有 `__next__`。**
2. **`__next__` 的职责**：报告当前值，**同时把状态往前挪一格**。
   `self.n -= 1; return self.n + 1` 就是"先推进、再报旧值"的紧凑写法。
3. **`StopIteration` 不是错误，是"结束信号"**。`for` 内部 `except StopIteration: break` 把它吃掉，
   所以循环静默结束；手动 `next()` 才需要自己接。
4. **迭代器/生成器只能遍历一次**。`list(迭代器)` 不是"复制"，是"**消费**"——
   位置是连续的：先 `next` 一个再 `list`，只会拿到剩下的。
5. **`yield` = 抛出值 + 把位置停在这里**。调用生成器函数**不执行函数体**，
   局部变量跟着生成器一起被保存。
6. **`finally` 保证的不是"是否输出"，而是"以哪种方式退出"**：跑完 / `break` / `close` / 异常，四条路都执行。
   生成器里开资源用 `with` 就够（`GeneratorExit` 会穿过 `with` 块）。
7. **推导式只用来"把一个集合变成另一个集合"**；有副作用（`print`、发请求、写文件）就写回 `for`。

## 备注（今天的坑）

- **迭代器 + `@retry` = 重试时内容没了**：重试传的是同一个参数，但迭代器已被耗掉一部分/全部 →
  **静默少处理，不报错**。修法：在函数内部新建迭代器，或直接传列表。
- `len(list(rows))` 之后再 `for rows` → 一行都没有（最典型的"一次性"事故）
- `next([1,2,3])` → `'list' object is not an iterator`（列表能 `for`，但不能 `next`）
- 惰性不能靠"有没有输出"证明 —— 只要 `list()` 在脚本里就一定有输出；**要看"读了"和标记的先后顺序**
- `iter[1,2]` 写法错（`iter` 是函数），必须 `iter([1,2])`
- `awk`（昨天）和 `iter` 的共同点：**参数/字段的位置错了不会报错，只是结果不对**

## 加练（SQL）

- 题目：查出"有订单无明细"的孤儿数据（`LEFT JOIN ... WHERE oi.id IS NULL`）
- 结果：✅ 1 行（`id=8, total_amount=0.00`）
- 卡在哪：**`INNER JOIN` 只留两边都匹配的行，孤儿会被直接丢掉**；
  必须 `LEFT JOIN` 把左表全保留、右表补 `NULL`，才能被 `WHERE ... IS NULL` 捉到

## 明天

Day 28：上下文管理器 + requests 封装 + logging

> 今天的 `try/finally + yield` 就是明天 `@contextmanager` 的实现；
> `log_calls` 里那些 `print` 明天换成 `logging`。
