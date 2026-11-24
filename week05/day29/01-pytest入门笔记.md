# Day 29 ｜ pytest 入门：assert / 用例发现 / -v -k

> 昨天复盘判据「第 3 阶没过」，今天先还账：填空版 25 分钟，错了 1 个空。

## 一、还账：填空版

### 1.1 六个空我填对了几个

- 5个

### 1.2 卡在哪一空，为什么

- 第一空
- 原因：只写到文件夹，没有写明文件名

### 1.3 跑通的输出（贴 `共 3 条 | 通过 3 | 失败 0`）

**输出：**

```test
共 3 条 | 通过 3 | 失败 0
```

## 二、pytest 的 assert

### 2.1 `assert 1 + 1 == 3` 在 pytest 和裸 python 里的两种报错（各贴一次）

**裸 python 输出：**

```text
AssertionError
```

**pytest 输出：**

```text
======================================= test session starts =======================================
platform win32 -- Python 3.12.10, pytest-9.2.0, pluggy-1.7.0 -- D:\Python312\python.exe
cachedir: .pytest_cache
rootdir: D:\work\qa-learning
collected 1 item

week05/day29/scripts/test_01_first.py::test_add FAILED                                       [100%]

============================================ FAILURES =============================================
____________________________________________ test_add _____________________________________________

    def test_add():
>       assert 1 + 1 == 3
E       assert (1 + 1) == 3

week04\day29\scripts\test_01_first.py:2: AssertionError
===================================== short test summary info =====================================
FAILED week05/day29/scripts/test_01_first.py::test_add - assert (1 + 1) == 3
======================================== 1 failed in 0.24s ========================================
```

**退出码`echo $?`输出：**

```text
1
```

- 127 = 命令找不到；1 = 有测试失败

### 2.2 为什么 pytest 能打出实际值（一句话）

- 因为 pytest 在导入测试文件时，把每一行 assert 的源码改写了一遍

### 2.3 四种 assert 写法，各自失败时看到什么

**①输出：**

```text
① E   assert 404 == 200
                                        ← 两边都是变量，值已经在表达式里，不额外给 where
```

**②输出：**

```text
② E   AssertionError: assert 'data' in {'code': -1, 'msg': 'bad'}
                                        ← 带 AssertionError: 前缀，右边整个字典打出来
```

**③输出：**

```text
③ E   AssertionError: assert 'timeout' is None
                                        ← 直接显示实际值
```

**④输出：**

```text
④ E   assert False
   E    +  where False = isinstance([1, 2, 3], dict)
                                        ← 还原了调用，告诉你它是怎么算出来的
```

### 2.4 为什么业务代码里不该用 assert

1. assert 会被 python -O 整段删掉
2. pytest 只会重写它收集到的测试模块和 conftest.py。在业务代码里写的 assert，不会被重写，报错还是光秃秃一个 AssertionError。

## 三、用例发现规则

### 3.1 哪些文件会被收集（列表 + 我的目录里实际收集到几个）

| 文件名 | 会被收集吗 | 为什么 |
| --- | --- | --- |
| test_login.py | ✅ | `test_` 开头 |
| login_test.py | ✅ | `_test` 结尾 |
| test_01_login.py | ✅ | 前缀是 `test_`，后面接数字没问题 |
| 01_notest.py | ❌ | 没有 `test_` 或者 `_test` |
| tests_login.py | ❌ | 是 `tests_` 不是 `test_` |
| testlogin.py | ❌ | 没有下划线 |
| test_login.txt | ❌ | 不是 .py |
| conftest.py | 特殊 | 是配置文件，不是测试（周三讲） |

**我目录里会被收集的：**

- my_test.py
- test_03_ok.py
- test_report.py

### 3.2 哪些函数/类会被收集

| 名称 | 会不会被收集 |
| --- | --- |
| test_login() | ✅ |
| test() | ✅（前缀就是 test） |
| test_ | ✅（虽然啥也没写） |
| my_test() | ❌ |
| Test_login() | ❌（大写 T，那是类） |
| testLogin() | ✅（test 后没有下划线也行，只要前四个字母是 test） |

- 函数名以 test 开头（不要求下划线）
- 类：必须以 Test 开头，且不能有 `__init__`。

### 3.3 `--collect-only` 的输出

**输出：**

```text
week05/day29/scripts/my_test.py::test_b
week05/day29/scripts/test_03_ok.py::test_a
week05/day29/scripts/test_report.py::test_user_1_ok
week05/day29/scripts/test_report.py::test_user_2_ok
week05/day29/scripts/test_report.py::test_status_404_returns_404
week05/day29/scripts/test_report.py::test_user_999_ok

6 tests collected in 0.34s
```

### 3.4 我故意留的"假测试"，为什么没被收集

1. `01_notest.py` 没有 `test_`或者`_test`
2. `test_04_wrongname.py`：文件被扫到了，但里面 **0 条用例** —— 文件合格、函数不合格
   （对比：`01_notest.py` 是文件本身不合格，压根没被扫）

### 3.5 我把两个演示文件改名的原因

`test_01_first.py` / `test_02_asserts.py` 是"故意失败"的演示，留着会让
`python -m pytest` 永远 5 红 —— 真失败和演示失败混在一起，就会开始无视红色。

处理：改名成 `demo_01_first.py` / `demo_02_asserts.py`
→ 不带 `test_` 前缀，pytest 完全不看它，但代码留着当记录。

**对比三种做法**：

| 做法 | 收集吗 | 能 python 直接跑吗 |
|---|---|---|
| 叫 `test_xxx.py` | ✅ | ✅（但会污染测试集） |
| 叫 `test_xxx.py` + `__main__` 守卫 | ✅ **还是收** | ✅ |
| **叫 `demo_xxx.py`** | ❌ | ✅ |

## 四、从 run_case 到 test_xxx

### 4.1 for 循环和 pytest 的五个差别（表格）

| 能力 | for 循环 | pytest |
| --- | --- | --- |
| 一条失败，其余继续 | 要自己 try/except（你昨天写了 12 行） | 天生 |
| 失败时看到期望/实际 | 自己往 return 里塞字段 | 拆 assert |
| 只跑其中一条 | 自己解析 sys.argv（你写了 3 行） | -k |
| 跑完给 CI 一个结论 | 自己 sys.exit(0/1/2) | 内置退出码（§5.5） |

### 4.2 我的 test_report.py（贴代码）

```py
import requests

BASE_URL = "https://httpbin.org"
TIMEOUT = 10


def get(uid):
    """把"发请求"收在一处，以后换成 ApiClient 只改这里"""
    return requests.get(BASE_URL + "/get", params={"userId": uid}, timeout=TIMEOUT)


def test_user_1_ok():
    r = get("1")
    assert r.status_code == 200


def test_user_2_ok():
    r = get("2")
    assert r.status_code == 200


def test_status_404_returns_404():
    # 这条不用 userId：httpbin 的 /status/404 一定会返回 404
    r = requests.get(BASE_URL + "/status/404", timeout=TIMEOUT)
    assert r.status_code == 404
```

### 4.3 故意失败那次的完整报告（贴出来）

**输出：**

```text
    def test_status_404_returns_404():
        # 这条不用 userId：httpbin 的 /status/404 一定会返回 404
        r = requests.get(BASE_URL + "/status/404", timeout=TIMEOUT)
>       assert r.status_code == 200
E       assert 404 == 200
E        +  where 404 = <Response [404]>.status_code

week04\day29\scripts\test_report.py:25: AssertionError
============================================================================================ short test summary info ============================================================================================
FAILED week05/day29/scripts/test_report.py::test_status_404_returns_404 - assert 404 == 200

```

### 4.4 我怎么读这份报告（期望/实际/来源/行号）

- 期望：`assert r.status_code == 200`
- 实际：`assert 404 == 200`
- 来源：`E        +  where 404 = <Response [404]>.status_code`
- 行号：`week04\day29\scripts\test_report.py:25`

## 五、命令与退出码

### 5.1 我常用的六条命令

```bash
# ① 跑全部（最常用）
python -m pytest

# ② 只跑某个文件 / 某个函数
python -m pytest week05/day29/scripts/test_report.py
python -m pytest week05/day29/scripts/test_report.py::test_user_1_ok

# ③ 详细模式：每条用例一行结果
python -m pytest -v

# ④ 只看会跑哪些，不执行
python -m pytest --collect-only -q

# ⑤ 按名字过滤
python -m pytest -k "user_1"

# ⑥ 首败即停
python -m pytest -x
```

- 文件::函数 这个写法（:: 双冒号）定位一条用例时最快：

```bash
python -m pytest week05/day29/scripts/test_report.py::test_user_1_ok -v
```

### 5.2 退出码 0 / 1 / 5 分别什么意思，和 Day28 我自定的 0/1/2 怎么对应

| 退出码 | pytest 的含义 | 和昨天的对照 |
| --- | --- | --- |
| 0 | 收集到用例，且全部通过 | 你写的「全过 → 0」✅ 一样 |
| 1 | 收集到了，但有失败 | 你写的「有失败 → 1」✅ 一样 |
| 2 | 被用户中断（Ctrl+C） | 你没处理，pytest 帮你区分了 |
| 3 | pytest 内部错误（或插件导入失败） | 环境问题，不是你的用例问题 |
| 4 | 命令行用法错误（参数错、conftest.py 导入失败） | 你写错了命令 |
| 5 | 一条用例都没收集到 | 你昨天自己发明的「没跑 → 2」 ⭐ |
| 6 | 警告数超过 --max-warnings | 少见 |

### 5.3 `echo $?` 实测结果

**输入：**

```bash
python -m pytest -k "根本不存在的名字"

echo $?
```

**输出：**

```text
5
```

## 六、自检 10 题

| # | 问题 | 一句话回答 |
| --- | --- | --- |
| 1 | 为什么用 python -m pytest 而不是 pytest（说两条） | 1：使用 python -m pytest 不用改 PATH。2：使用 python -m pytest 是指定python 不会跑错python |
| 2 | assert 1 + 1 == 3 在 pytest 里为什么能显示 (1 + 1) 而不只是 AssertionError | 因为pytest在导入的时候重写了一遍 |
| 3 | pytest 的文件/函数/类各要满足什么名字规则 | 文件：以`test_`开头，或者以`_test`结尾。函数：以`test`开头。类：必须以 Test 开头，且不能有 `__init__` |
| 4 | 测试函数加了参数会报什么错，为什么 | 报错：`E       fixture 'username' not found`。原因：pytest 看到参数，会认为要一个同名的 fixture |
| 5 | --collect-only 是干什么的，什么时候先用它 | 它不执行任何测试，只回答"这一跑会动到哪些"，在写完测试之后用，可以提前发现"文件没被识别""函数名写错"这类问题 |
| 6 | -k 和 :: 各自怎么用，差别是什么 | -k是按照名字筛选，::是文件::函数 |
| 7 | -s 解决什么问题 | print 了东西却看不见。可以不捕获 print，直接显示 |
| 8 | 退出码 0 / 1 / 5 分别是什么，5 为什么不能算成功 | 5 是一条用例都没收集到，相当于什么都没干，不能算作成功 |
| 9 | 为什么业务代码里不该写 assert | 会被 python -O 整段删掉。业务代码里写的 assert，不会被重写，报错还是光秃秃一个 AssertionError |
| 10 | 一条用例里为什么只放一个 assert（或一组强相关的） | 可以更好的定位报错位置。如果一条用例里塞入多种 assert，一旦报错不知道是哪个出现问题 |

## 七、还没搞懂的

- 无

## 八、今日 3 题

- Q050 | pytest 怎么知道哪些函数是测试 | 文件 `test_*.py` 或 `*_test.py`；函数以 `test` 开头（惯例 `test_`）；类 `Test` 开头且没有 `__init__` | 🔁
- Q051 | pytest 的 assert 为什么比 unittest 的 assertXxx 好用 | 一个裸 assert 通吃所有比较，不用记 30 个方法名；断言重写让失败时打印中间值 | 🔁
- Q052 | pytest 退出码 5 是什么意思，为什么不能当成功 | 没收集到任何用例；测试根本没跑，比失败更该报错 | 🔁

> **写完后跑** `python tools/sync_qa.py`

- 加练：Shell 统计 pytest 结果，卡在 "=" 的运用上。"=" 两边有空格是执行命令，没有空格才是赋值。
