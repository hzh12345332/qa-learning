# Day 29 ｜ pytest 入门：assert / 用例发现 / -v -k

产出：

| 文件 | 内容 |
|---|---|
| `01-pytest入门笔记.md` | 笔记主体（330 行，八章） |
| `scripts/report_b0.py` | **B0 填空版**：还 11/22 复盘「第 3 阶没过」的账（25 min / 5-6 空对） |
| `scripts/test_report.py` | **4 条真用例**：`user_1` / `user_2` / `status_404` / `user_999` + `get()` 辅助函数 |
| `scripts/test_03_ok.py` | `test_` 开头 → **会被收集** |
| `scripts/my_test.py` | `_test` 结尾 → **也会被收集**（证明后缀也认） |
| `scripts/test_04_wrongname.py` | 文件被扫到，但**里面 0 条用例**（函数名不合格） |
| `scripts/01_notest.py` | `test_` 开头、`_test` 结尾**都不满足** → 压根不被扫 |
| `scripts/demo_01_first.py` | 演示：`assert 1 + 1 == 3`（**改名后不参与收集**） |
| `scripts/demo_02_asserts.py` | 演示：四种 assert 的四种报错（**改名后不参与收集**） |
| `scripts/demo_01_plain.py` | 裸 `python` 跑，只有 `AssertionError`；带 `__main__` 守卫 |
| `data/report_b0.json` | 3 条全 pass 的产物（不入库） |

**跑一遍**：

```bash
cd /d/work/qa-learning
python -m pytest week05/day29/scripts -q
# 6 passed in 8.33s        退出码 0
```

## 今天搞清的八点

1. **`python -m pytest`，不是 `pytest`**：`D:\Python312\Scripts` 不在 PATH，裸 `pytest` 是 `command not found`；
   而且 `python -m` 会把**当前目录加进 `sys.path`**（官方文档），裸命令不加 —— 这决定你 `import` 自己的模块会不会失败。
2. **断言重写的效果**：pytest 在**导入测试文件时改写每一行 `assert`**，所以失败能看到 `assert (1 + 1) == 3`；
   而**裸 `python` 跑只有一句 `AssertionError`**。
3. **`where` 只在“值需要算”时出现**：变量/常量比较不给（`assert 404 == 200`）；函数调用/属性访问才给
   （`where 404 = <Response [404]>.status_code`）。
4. **发现规则**：文件 `test_*.py` **或** `*_test.py`；函数**以 `test` 开头**（不要求下划线）；类 `Test` 开头且**不能有 `__init__`**。
   **“数字开头”不是规则** —— `01_test.py` 因为以 `_test` 结尾，照样被收集。
5. **测试函数不能带参数** —— 会被当成要一个同名 fixture，报 `fixture 'xxx' not found`。
6. **`--collect-only` 不执行测试，但会 `import` 文件** → 模块级代码照样跑。
   **这才是“加 `__main__` 守卫”和“改文件名”的区别**：守卫只挡 import 时执行，**挡不住被当成测试收集**。
7. **退出码**：0 全过 / 1 有失败 / 2 中断 / 3 内部错 / 4 用法错 / **5 一条用例都没收集到**；
   **5 不能当成功** —— 就是你 11/22 自己发明的「没跑 → 2」。另外 **127 是 shell 的“命令找不到”**，不是 pytest 的码。
8. **业务代码不写 `assert`**：① 不被重写，报错光秃秃；② `python -O` 会整段删掉；③ 全变成 `AssertionError`，上层**区分不了错误类型**。
   业务代码用 `raise`，`assert` 只写在测试里。

## 备注（今天的坑）

- **B0 第 ① 空只写到目录** `week05/day29/data`（漏 `report_b0.json`）→ `open()` 报 `PermissionError`
  （Windows 把“把目录当文件写”报成权限问题；Linux 上是 `IsADirectoryError`）
- **笔记里退出码写成 127** —— 其实是 shell 的 `command not found`，pytest 断言失败是 **1**
- **加练 shell 脚本第一版全是语法错**：`LOG = /tmp/pytest.out`（等号两边有空格）→ bash 把 `LOG` 当命令执行；
  而且 `LOG` 还**撞了环境变量**（`$LOG` 悄悄指向了 `D:\backup\...\restart-log.txt`），变量没赋上也不报错
- **演示用例留在 `test_` 目录里** → 每次全量 `5 failed`，真失败和演示失败混在一起，会开始无视红色 → 改名 `demo_`
- **`--collect-only` 的输出贴了旧的 11 条**，改名后实际是 6 条 —— 代码改了、证据没改

## 加练（Shell）

- 题目：统计 pytest 输出的 `PASSED` / `FAILED` 数，有失败就 `exit 1`
- 结果：✅ 两个分支都验过

| 日志 | 输出 | 退出码 |
|---|---|---|
| 6 passed / 0 failed | `PASSED: 6  FAILED: 0` | **0** |
| 2 passed / 1 failed | `PASSED: 2  FAILED: 1` | **1** |

- 卡在哪（四条 shell 规矩）：
  1. **赋值时等号两边不能有空格**：`LOG=/tmp/pytest.out`
  2. 取命令输出用 `$(...)`，`$` 前不加空格
  3. `if` 的条件用 `[ ]`，**括号内外都要空格**：`if [ "$f" -gt 0 ]`
  4. `if ... then ... fi`；退出码用 `exit 1`，不是 `echo 1`

## 明天（11/24 周二）：`fixture`

**今天把“发请求”收进了 `get()` 函数。明天的问题**：

> 三个测试文件都要 `BASE_URL`、都要 `TIMEOUT` —— 每个文件复制一份 `get()` 吗？

**明天的答案：`fixture`。**

| 今天 | 明天 |
|---|---|
| `get()` 是普通函数，每个文件各复制一份 | `fixture` 写一次，所有文件共用 |
| 每条用例自己 `requests.get(...)` | `def test_x(client):` —— 参数一写，pytest 自动注入 |
| 告一段落就断开 | `yield` 版 fixture：前半段准备、后半段清理 |
| 作用域只有“这个函数” | `function` / `module` / `session` 三级 |

> 今晚 3 分钟想一件事：把 `with ApiClient(cfg["baseUrl"]) as client:` 做成 fixture，
> **`yield` 应该写在哪一行？**（`yield` 前是 `__enter__`，后是 `__exit__` —— Day 28 学过这个对应关系。）
