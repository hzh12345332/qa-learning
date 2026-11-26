# Day 32 ｜ parametrize：users.csv 接入 + ids

产出：

| 文件 | 内容 |
|---|---|
| `01-parametrize笔记.md` | 笔记主体（277 行，九章） |
| `scripts/test_01_first_parametrize.py` | 1 函数 → 3 条用例；另一组用 **xfail** 标记的故意失败（演示失败报告） |
| `scripts/test_02_two_cols.py` | **一次传多列**：`userId` + `expected`，接真实 httpbin |
| `scripts/test_03_from_csv.py` | **从 `users.csv` 读** → 加一行 CSV 就多一条用例 |
| `../conftest.py` | 今天从 `day31/` **上移**到 `week05/`，day32 及以后都能用 |

**跑一遍**：

```bash
cd /d/work/qa-learning
python -m pytest week05/day32 -q
# 11 passed, 1 xfailed        退出码 0
```

## 今天搞清的八点

1. **`parametrize` 三要素**：参数名字符串（`"userId,expected"`）+ 数据组列表（每组一个元组）+ 函数签名同名收参数。
2. **那个字符串是"拆包说明"**：它决定"这一组数据按顺序拆给哪几个参数名"，**不决定分几组**（分几组看列表有几项）。
3. **用例名 = 函数名 + `[这组的值]`**：单值 `[1]`、多列 `[1-200]`（用 `-` 拼）、`ids=` 可自定义。**参数名一个字都不会出现在用例名里。**
4. **函数参数有两条注入通道**：名字有 fixture → 从 fixture 来；名字在 parametrize 名单里 → 从数据来；都匹配不上 → `fixture 'xxx' not found`。
   **同名时 `parametrize` 静默覆盖 fixture**（不报错，更危险）。
5. **失败时 pytest 多给一行** `a = 2, b = 404` —— 这组的所有参数值直接列出来。手写两个函数就得自己塞进断言消息。
6. **`load_cases()` 必须在模块顶层调用**：`parametrize` 的第二个参数在**收集期**就要有值，放用例里（运行时）来不及。
7. **CSV 读出来全是字符串**：`expected` 必须 `int()`，否则 `200 == "200"` 永为假。
8. **空数据列表 → 全 SKIPPED**（`[NOTSET]`，退出码 **0**），不是通过也不是报错 —— **"什么都没测"被当成"全过"**。

## 备注（今天的坑）

- **`day32` 用不了 `client`/`cfg`** → 它们在 `day31/conftest.py` 里，**兄弟目录不可见** → `git mv` 到 `week05/conftest.py` 解决
- **以为两个数据组会"互相比较"** → 其实每组**独立跑一遍函数体**，互不知情
- **`-k "1-200"` 是模糊匹配** → 顺带命中 `[11-2000]`，要精确就写 `-k "[1-200]"`
- **空列表静默跳过** → 用 `assert rows, "users.csv 里没有数据…"` 防住
- **`DATA` 路径少打一个字母**（`da` 不是 `data`）→ `FileNotFoundError`，收集期就挂
- **演示失败留在全量里** → 用 `pytest.mark.xfail` 标记（退出码 0），想看真实报告加 `--runxfail`

## 硬指标验收（今天的核心）

**判据：「新加一个用例只改数据文件，不改代码。」**

| 步骤 | 用例数 |
|---|---|
| 原始 `users.csv`（3 行） | 3 条 |
| **加一行 `3,200`**（不动任何 `.py`） | **4 条** |
| 再把某行 `expected` 改错 | **只那条失败**，其他照跑 |

`users.csv` 第 4 行 `3,200` **留在库里**当第四条用例（已验证来源是"硬指标实验"）。

## 加练（Shell）

- 题目：从 pytest 输出里统计"每个函数跑了几组"
- 结果：✅ 两个分支都验过

| 日志 | 输出 | 退出码 |
|---|---|---|
| 有 4 组 | `test_user_get:4组` | **0** |
| 空日志 | 屏幕警告「没有任何参数组…」 | **1** |

- 卡在哪（两个坑）：
  1. **`[^]]` 看不懂**（取反集合里第一个 `]` 是字面量）→ 改用 `[^ ]*`（避开空格）绕过去
  2. **`[ "total" -eq 0 ]` 少了 `$`** → 报 `total: integer expected`（`"total"` 是字面字符串）
- 额外学到：**正则的"左边界"比右边界重要** —— 少了 `::` 锚点会把文件名 `test_03_from_csv` 和 `.pytest_cache` 一起抓进来

## 明天（11/27 周五）：重写 `report_class.py` 成 pytest 版

**本周三个地基今天齐了**：

| 天 | 建好的东西 | 在重写里干什么 |
|---|---|---|
| 周三 | `conftest.py` + `cfg`（读 `config.json`） | 配置不再写死 |
| 周二 | `client` fixture（`Session` + `yield`） | 连接复用 + 自动关闭 |
| **今天** | `parametrize` + `users.csv` | **数据不再写死** |

| day28 的 `report_class.py` | 明天的 pytest 版 |
|---|---|
| `load_config()` 方法 | `cfg` fixture（conftest） |
| `_do_request()` + `run_case()` | 一个 parametrize 的 `test_` |
| `run_all()` 里的 `for row in csv...` | **`parametrize` 展开** |
| `summary()` 打印 | pytest 的结果统计 |
| `sys.exit(0/1/2)` | pytest 退出码 |

> 今晚 3 分钟想一件事：`report_class.py` 里"失败时把 error 写进结果"那个分支，
> **换成 pytest 之后该怎么表达？**（提示：断言失败 vs 异常，Day 30 §6.1 分过）
