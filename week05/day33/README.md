# Day 33 ｜ 把 `report_class.py` 重写成 pytest 版

产出：

| 文件 | 内容 |
|---|---|
| `01-框架重写笔记.md` | 笔记主体（385 行，八章） |
| `scripts/test_report_pytest.py` | **6 行、零 import**，一个函数跑 4 组数据 |
| `../conftest.py` | 加 `load_cases()` + `pytest_generate_tests`（数据层）；**`only_in_sub` 原样没动** |
| `week04/day28/scripts/report_class.py` | 删掉 `sys.exit()` 后面那三行死代码 |

**跑一遍**：

```bash
cd /d/work/qa-learning

python -m pytest week05/day33 -q
# 4 passed                      退出码 0

python -m pytest week05 -q
# 40 passed, 1 xfailed          退出码 0（旧用例没被搞挂）
```

## 今天搞清的八点

1. **105 行 → 9 行，不是变简单了，是职责分家了。** 配置（`cfg`）/ 连接（`client`）/ 数据（钩子）/ 用例（只写断言）各归各层。判据是「改一个东西动几个文件」。
2. **`pytest_generate_tests` 是"按名字注入"**：测试函数参数名写 `row`，钩子就把 CSV 每一行塞进去；写成 `case` 就不认（收集期 `ERROR: fixture 'case' not found`）。
3. **`pytest_generate_tests` 才是钩子，`metafunc.fixturenames` 是"当前函数要用的所有名字"的列表** —— 钩子靠读它决定要不要注入。
4. **旧版 `try/except` 的三个目的全不成立**：① pytest 天然不中断 ② `type(e).__name__` 只留一个词 ③ 报告换 `junitxml` 了。
5. **`try` 只挡网络异常，挡不住代码 bug**：`int("abc")` 写在 try 外面 → `ValueError` 穿出去 → 循环当场断（实测只跑 1 条）。
6. **"保护范围" vs "隔离机制"**：同一份坏数据，pytest 版 4 条全跑、只有 `[2]` 变红。旧版靠 try 写在哪决定保护范围，pytest 是结构保证 —— **不用预判会出什么错**。
7. **`error="ConnectTimeout"` 省的不是篇幅，是排查信息**：pytest 给的是四层异常链（socket → urllib3 → urllib3 → requests），一条 traceback 就 646 行。
8. **报告该长就长，压缩发生在展示层**：`--tb=short` 224 行 / `--tb=line` 52 行 / `--tb=no` 7 行 —— 不是不采集，是换粒度展示。

## 备注（今天的坑）

- **`sys.exit()` 后面三行死代码** —— 在文件里待了 5 天，跑过、也"读懂"过，没人发现它从没执行
- **`| tail` 会吃掉退出码** —— `python x.py | tail -5; echo $?` 拿到的是 `tail` 的 0（第一次把 A 组退出码读错了）
- **`timeout=10` 时 A 组跑了 87 秒** —— 4 条 × 9 次请求 × 每次 2.4 秒；做连不上的实验前先把 timeout 改 1
- **第一次实验做偏了** —— 把 `cfg` 拼成 `cgf` 只能证明"拼错会报错"；要证明钩子的名字约定，必须把 `row` 换成 `case`
- **`logger.info` 写在请求之后** —— 异常路径上永远不执行，故障现场是空白，看起来像"根本没跑到"
- **`report.xml` 在 repo 根，`.gitignore` 没兜住** → 已补 `report.xml` / `reports/` 两条规则
- **两套装饰器同时在跑** —— `ApiClient.get` 用的是 `api_client.py` 自己那份（`__module__` 实测），重试套了两层 → **3×3 = 9 次请求**

## 硬指标验收（今天的核心）

**判据：「把 `report_class.py` 用 pytest 重写：fixture 管配置与 client、parametrize 管 CSV 每一行、conftest 做分层。
新加一个用例只改数据文件，不改代码。」**

| 步骤 | 用例数 | 改了几个 `.py` |
|---|---|---|
| 原始 `users.csv`（4 行） | 4 条 | — |
| **追加 `4,500`**（httpbin 恒返回 200，必然失败） | **5 条**（`[4]` 自动出现） | **0 个** |
| 把 `2,200` 改成 `2,404` | 4 条，只有 `[2]` 变红 | **0 个** |
| 验完删掉 `4,500` | 4 条 | 0 个 |

> 第 4 行 `3,200` 是 Day32 的正式用例，**留在库里**。
> `4,500` 是今天的一次性耗材，已删。

## 加练（SQL）—— 今天没做，11/28 早上补

- **题目**：用一条 SQL 复刻 pytest 的结尾行 —— `总数 | 通过 | 失败` = `4 | 3 | 1`
- **题面 + 参考实现**：`G:\DSH\逐日手册\Day33-逐日执行手册.docx` §12
- **状态**：⏳ pending —— 明天（11/28）早上 15 分钟内补完，补完再记进 `练习/README.md`
- **本周加练**：11/23 Shell ✅ ｜ 11/24 SQL ✅ ｜ 11/25 断言 ✅ ｜ 11/26 Shell ✅ ｜ 11/27 SQL ⏳
  已达标 **4/4**，明天补的是第 5 次（加做，不影响达标）

## 明天（11/28 周六）：框架分层续 + 骨架跑通一条用例

重排表 #20 第二天。今天做完的是"能跑的版本"，明天做"能长大的版本"。

| 今天有什么 | 明天要加什么 |
|---|---|
| `DATA_PATH` 写死在 conftest | 环境切换 `--env=test/prod` |
| 一条断言 `status_code == expected` | 断言分级：状态码 / 业务码 / 字段值 |
| 失败只有 traceback | 失败快照（`pytest_runtest_makereport`） |
| `--junitxml` 手敲参数 | `pytest.ini` 配置化 |
