# Day 30 ｜ fixture：作用域 / yield 清理 / 改造 test_report

产出：

| 文件 | 内容 |
|---|---|
| `01-fixture笔记.md` | 笔记主体（412 行，九章） |
| `scripts/test_01_first_fixture.py` | 第一个 fixture：参数名 = 需求，**没有一行调用** |
| `scripts/test_02_yield.py` | `yield` 版：`[setup]`/`[teardown]` 前后各一次 |
| `scripts/test_03_scope.py` | 三级作用域对照（3 个 fixture + 4 条用例） |
| `scripts/test_03b_autouse.py` | `autouse` + fixture 依赖链（`api(base_url)`） |
| `scripts/test_04_report_fixture.py` | **改造版**：`cfg` + `client` session 级，`Session` 只建一次 |
| `scripts/demo_06_error.py` | **两种 ERROR 的复现**（`demo_` 开头，不进全量收集） |
| `data/tmp_demo.txt` | `yield` 用例的产物（不入库） |

**跑一遍**：

```bash
cd /d/work/qa-learning
python -m pytest week05/day30/scripts -q
# 10 passed in 7.52s        退出码 0
```

> `demo_06_error.py` **不在**这 10 条里 —— 要跑它得显式指定：
> `python -m pytest week05/day30/scripts/demo_06_error.py -q` → `2 errors`（设计如此）

## 今天搞清的九点

1. **fixture 是"声明需求"，不是"调函数"**：`def test_x(client)` 的参数名就是需求，pytest 找同名 fixture 先执行、再把返回值塞进来。
2. **`yield` 把函数劈成两半**：`yield` 之前 = setup，值交给用例，`yield` 之后 = teardown。
   **用例失败时 teardown 照样执行**（实测 `FAILED [teardown] 关掉文件`）。
3. **`yield` 版 fixture 就是 `with` 的测试版**：`__enter__` ↔ yield 前，`__exit__` ↔ yield 后。
   所以写 `with ApiClient(...) as c:` 时，**`yield` 要写在 `with` 里面**。
4. **三级作用域**：`function`（每条）/ `module`（每个文件）/ `session`（整轮）。
   **`module` 的边界是文件** —— 多文件时它会建 N 次，`session` 只建 1 次。
5. **teardown 是逆序的**：setup 从外往里，teardown 从里往外 —— **一个栈**。
6. **`autouse=True` 在最外层**（setup 最先、teardown 最后），而且**参数里看不到它**。
   只用于"全局卫生"（日志/清理/重置），**数据依赖要写参数**，否则依赖不可见。
7. **fixture 依赖 fixture 靠参数名**：`def api(base_url):` 就是声明依赖，用例只要 `api`，`base_url` 自动跟上。
8. **三种失败要分清**：`FAILED`（跑了，断言没过，退出码 1）／`ERROR at setup`（没跑起来，退出码 1）／`ERROR: file not found`（**命令打错**，退出码 4）。
9. **`--setup-show` 看 pytest 的调度**（顺序/依赖/作用域标记 `F`/`M`/`S`），**`-s` 只看你自己 `print` 的东西**。
   没写 `print` 的 fixture（比如 `base_url`）在 `-s` 里**完全看不见** —— 这就是为什么排查 fixture 要用 `--setup-show`。

## 备注（今天的坑）

- **文件里只写了 fixture、忘了写用例** → `collected 0 items`，**零报错**，但一条也没跑
- **故意 ERROR 的演示文件用了 `test_` 开头** → 每次全量都会 red → 改名 `demo_06_error.py`
  （实测：**显式指定路径照样能跑**，扫目录才不收）
- **`data/tmp_demo.txt` 会被提交** → `.gitignore` 补 `week*/**/data/tmp_*.txt`
- **把"文件不存在"当成 fixture 的 ERROR** → 那其实是**命令打错**（退出码 4），和 `ERROR at setup` 不是一回事
- **`scope="session"` 放有状态的东西** → 一个用例改脏了，下一个莫名失败（单跑绿、一起跑红）

## 改造 test_report.py（今天的重点）

| | 改造前（day29） | 改造后（day30） |
|---|---|---|
| 配置 | 模块常量 `BASE_URL` | `cfg` fixture（session 级） |
| 发请求 | 每条用例 `r = get("1")` | 参数声明 `client, cfg` |
| 连接复用 | ❌ 每次新建 | ✅ `requests.Session`，整轮只建一次 |
| 清理 | ❌ | ✅ `yield` 后 `s.close()` |
| 跑通 | — | `3 passed`，`[setup] Session 建好了` **只出现一次** |

**把 `client` 的 scope 改成 `function` 再跑** → `[setup]` 变 3 次 —— 亲手确认 scope 真在起作用。

## 加练（SQL）

- 题目：**每个用户最近一笔订单**（`PLAN.md` 待办池里「SQL 后 17 题」的窗口函数题）
- 卡在哪：**想"GROUP BY 分组 → 组内按时间倒序 → 取第一条"**
  - `GROUP BY` 是**折叠**不是筛选，每组压成一行，其余行直接消失，**没有"第一条"这个概念**
  - **`ORDER BY` 在 `GROUP BY` 之后执行**，所以"先排序再分组"在 SQL 里不存在
  - `GROUP BY + MAX(created_at)` 只能拿回时间，**拿不到那一行的 `order_id`/`amount`**
- 解法：**先造序号，再按序号筛**

```sql
WITH t(...) AS (...),
ranked AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn
    FROM t
)
SELECT user_id, order_id, amount, created_at FROM ranked WHERE rn = 1;
```

- **必须套一层**：窗口函数在 `WHERE` 之后才算，同一层不能 `WHERE rn = 1`
- 三种排名函数的区别：`ROW_NUMBER`（1 2 3，绝不重复）／`RANK`（1 1 3，并列跳号）／`DENSE_RANK`（1 1 2 3，并列不跳号）

## 明天（11/25 周三）：`conftest.py` 分层 + 配置注入

**今天 `cfg` 和 `client` 写死在 `test_04_report_fixture.py` 里，只有这一个文件能用。**

| 今天 | 明天 |
|---|---|
| fixture 写在测试文件顶部 | 挪到 **`conftest.py`**，同目录所有测试文件自动可用 |
| `cfg` 是硬编码字典 | 改成**读 `week04/day23/data/config.json`** |
| 一个文件装所有 fixture | 根 `conftest.py` + 子目录 `conftest.py` 分层 |
| — | **30 分钟从零手写**（周三惯例） |

> 今晚 3 分钟想一件事：`cfg` 要读 `config.json`，那它该依赖什么？
> 提示：Day 23 你写过 `load_config(path)` —— fixture 里能不能直接用它？
