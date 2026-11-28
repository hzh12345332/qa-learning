# Day 34 ｜ 从「能跑」到「能定位」

产出：

| 文件 | 内容 |
|---|---|
| `01-骨架分层笔记.md` | 笔记主体（339 行，八章） |
| `conftest.py` | `--env` 参数 + `cfg`(session) + `client`(function) + `trace` + `pytest_runtest_makereport` |
| `config/test.json` `config/prod.json` | 两份环境配置 |
| `scripts/test_04_skeleton.py` | 骨架：4 条 parametrize + 三层断言 + `@pytest.mark.smoke` |
| `scripts/test_03_asserts_fail.py` | 1 过 3 xfail（缺字段 / 多出字段 / 业务值） |
| `scripts/test_cfg_follows_env.py` | `--env` 自检 |
| `scripts/t_snap.py` | 故意失败的演示（**不以 `test_` 开头，不参与收集**） |
| `week05/common/asserts.py` | 五个断言函数（三层 + 多余字段检查） |
| `../../pytest.ini` | **repo 根**的 pytest 配置 |

**跑一遍**：

```bash
cd /d/work/qa-learning

python -m pytest                    # 7 passed, 3 xfailed     退出码 0
python -m pytest -m smoke           # 只跑标了 smoke 的那 4 条
python -m pytest --env=prod         # 换 prod 配置跑
python -m pytest --env=uat          # 退出码 4（命令行用法错误）
```

## 今天搞清的八点

1. **`pytest.ini` 四个键**：`testpaths`（默认路径）/ `addopts`（默认参数）/ `pythonpath`（模块搜索路径）/ `markers`（注册标记）。**写在 repo 根，`rootdir` 才对。**
2. **`ERROR` + `Interrupted` ≠ `FAILED`**：前者是**收集期**出错，**一条用例都没跑**；后者是跑了但挂了。
3. **`--env` 三步数据流**：`pytest_addoption` 注册 → `request.config.getoption()` 读 → fixture 拼配置文件名。`choices=` 挡住错拼，**错拼退出码 4 不是 1**。
4. **三层断言**：传输（状态码）→ 结构（是不是 JSON / 有没有字段）→ 业务（字段值）。**顺序不能乱** —— 500 的时候先报「JSON 解析失败」会掩盖真因。
5. **「缺字段」和「多出字段」是集合减法的两个方向**：`required - actual` vs `actual - required`。只换个遍历对象，就是另一个检查。
6. **失败快照靠两个钩子**：`requests.Session.hooks["response"]` 记每次请求 + `pytest_runtest_makereport` 在失败时塞进 `rep.sections`。**缺第一个就没内容可塞。**
7. **作用域按「要不要承载单条用例的状态」定**：`cfg` 只读一份 → **session**；`client` 要给每条用例独立记录 → **function**。
8. **断言通过时是沉默的**：`1 passed` 里没有任何数字。想看值必须 `print` + `-s`；不想看数字但想验证，就用 `assert`。

## 备注（今天的坑）

- **`cfg` 一开始写成 `function` 级** → 每条用例都读一次 JSON，`[cfg] 加载了` 打印 **8 次**；改回 `session` 后变 **1 次**
- **往已有的 xfail 用例里加断言** → 前面的 `check_fields` 先挂，**新加的 `check_no_extra_fields` 永远执行不到**（`--runxfail` 才看出来）
- **`--env=uat` 退出码是 4** —— 差点以为「跑不出结果」，其实是真的一个测试都没启动
- **`tasklist` 查不到 WPS，但 docx 确实被锁** → 改成「直接试打开文件」判断占用，比查进程名可靠
- **VS Code 对中文全角标点画黄框** → 不是代码问题，配 `editor.unicodeHighlight.ambiguousCharacters: false` 关掉
- **手册里的 `7 passed` 是示例环境的数字** → 判据应该是 `3 xfailed`（那三条从 failed 变 xfailed），不是 passed 的数量

## 硬指标验收

**本周硬指标**：「把 `report_class.py` 用 pytest 重写：fixture 管配置与 client、parametrize 管 CSV 每一行、conftest 做分层。」

| 层 | 落在哪 | 今天补上了什么 |
|---|---|---|
| 配置 | `pytest.ini` + `--env` + `cfg` | **环境可以一条命令切换** |
| 连接 | `client` fixture | **每条用例独立 Session + 自动记请求** |
| 数据 | `pytest_generate_tests` + `users.csv` | —（Day 33 完成） |
| 用例 | `test_04_skeleton.py` | **只写断言，四行三层** |

**骨架一条用例，串起了四天的成果**：

```python
@pytest.mark.smoke
def test_user_get(client, cfg, row):        # row 来自 Day 32 的 CSV 注入
    r = client.get(cfg["baseUrl"] + cfg["endpoint"],   # cfg 由 --env 决定
                   params={"userId": row["userId"]},
                   timeout=cfg["timeout"])
    check_status(r, 200)                    # 第 1 层
    data = check_json(r)                    # 第 2 层
    check_fields(data, ["args", "headers", "url"])
    check_value(data["args"], "userId", row["userId"])   # 第 3 层
```

## 加练

| 日期 | 技能 | 题目 | 状态 | 卡在哪 |
|---|---|---|---|---|
| 11/27 | SQL | 用一条 SQL 复刻 pytest 结尾行（CTE 造数据） | ✅ | 写了三条独立 SELECT；聚合函数吃的是「逐行表达式」不是子查询 |
| 11/28 | 断言 | 给 `check_fields` 加「多余字段」检查 | ✅ | 新检查塞进旧 xfail 用例末尾 → 前面先挂，新函数永远跑不到；**必须单独一条用例** |

**11/28 的收获**：`check_no_extra_fields(data, allowed)` —— 集合减法反方向，只换了遍历对象。
**更大的收获是一条规则**：**一条用例只验证一个失败点**，否则后面的断言永远没被执行。

## 明天（11/29 周日）：第五周复盘

**不学新东西。** 三件事：

| 事 | 产出 |
|---|---|
| 写周复盘 | `week05/周复盘/2026-11-23至11-29.md` |
| 逐条对照本周硬指标 | 用 `PLAN.md` 的原话，看哪句兑现了 |
| 给第六周（项目 1）定范围 | 只定**第一步**，别规划 7 天 |

**复盘时回答这个问题**：

> 现在把这套东西交给一个陌生人，他能看懂「怎么跑、跑到哪、挂了查哪」吗？
> 能 → 这叫**框架**。不能 → 还只是**一堆能跑的脚本**。
