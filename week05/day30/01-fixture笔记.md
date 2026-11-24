# Day 30 ｜ fixture：作用域 / yield 清理 / 改造 test_report

## 一、fixture 是什么

### 1.1 从"调函数"到"要参数"，差在哪（贴两版代码）

**调函数：**

```py
def base_url():
    return "https://httpbin.org"


def test_base_url(): 
    f = base_url()
    assert f.startswith("http")
```

**要参数：**

```py
import pytest

@pytest.fixture
def base_url():
    return "https://httpbin.org"


def test_base_url(base_url):          # ← 参数名 = fixture 名
    assert base_url.startswith("http")
```

- 差在哪：调函数版需要写调用代码。要参数版直接把函数名拿来用

### 1.2 参数名和 fixture 名的关系

- 参数名必须和 fixture 名一模一样。 差一个字母就是 fixture 'xxx' not found

### 1.3 `return` 版和 `yield` 版的区别

| 写法 | 能准备 | 能清理 | 能共享 | 失败时也清理 |
| --- | --- | --- | --- | --- |
| return | ✅ | ❌ | ✅ | — |
| yield | ✅ | ✅ | ✅ | ✅ |
| 在用例里手写 | ✅ | 要 try/finally | ❌ | 要自己写 |

## 二、yield 的 setup / teardown

### 2.1 我的 `temp_file` fixture（贴代码 + `-s` 的输出）

**输入：**

```py
import pytest

@pytest.fixture
def temp_file():
    print("  [setup] 造一个临时文件")
    f = open("week05/day30/data/tmp_demo.txt", "w", encoding="utf-8")
    f.write("hello")
    yield f                                  # ← 这里"停顿"，把 f 交出去
    print("  [teardown] 关掉文件")
    f.close()


def test_can_write(temp_file):
    print("    >> 用例开始")
    temp_file.write(" world")
    assert True
```

**`python -m pytest week05/day30/scripts/test_02_yield.py -v -s`输出：**

```text
week05/day30/scripts/test_02_yield.py::test_can_write   [setup] 造一个临时文件
    >> 用例开始
PASSED  [teardown] 关掉文件
```

### 2.2 故意让用例失败，teardown 还执行吗？（贴结果）

- 用例失败 teardown 也会执行

**输入：**

```py
def test_can_write(temp_file):
    print("    >> 用例开始")
    temp_file.write(" world")
    assert False
```

**输出：**

```text

week05/day30/scripts/test_02_yield.py::test_can_write   [setup] 造一个临时文件
    >> 用例开始
FAILED  [teardown] 关掉文件
```

### 2.3 `yield` 和 `with` 的对应关系（画个表）

| 方面 | with | yield fixture |
| --- | --- | --- |
| 准备 | `__enter__` | yield 之前 |
| 交出资源 | `__enter__` 的返回值 | yield 的值 |
| 清理 | `__exit__` | yield 之后 |
| 清理保证执行 | ✅（包括异常） | ✅（包括用例失败） |

### 2.4 在 `with` 版 fixture 里，`yield` 写哪一行

- yield 写在 with 的里面 —— 这样 with 负责关，fixture 负责递。

**例如：**

```py
@pytest.fixture
def client(cfg):
    with ApiClient(cfg["baseUrl"]) as c:      # Day 28 写的那个
        yield c                                # ← yield 在 with 里面
```

## 三、作用域

### 3.1 三级作用域的实测输出（贴完整）

**输出：**

```text
week05/day30/scripts/test_03_scope.py::test_a   [setup]    shared_config
    >> test_a
PASSED  [teardown] shared_config

week05/day30/scripts/test_03_scope.py::test_b   [setup]    shared_config
    >> test_b
PASSED  [teardown] shared_config

week05/day30/scripts/test_03_scope.py::test_c   [setup]    session_flag (session)
  [setup]    module_client (module)
    >> test_c
PASSED
week05/day30/scripts/test_03_scope.py::test_d     >> test_d
PASSED  [teardown] module_client (module)
  [teardown] session_flag (session)
```

### 3.2 我从输出里读出的四条结论

1. function 作用域：每条用例都重新建一次 `shared_config` 在 `test_a`、`test_b` 各建了一次 —— 中间那道 [teardown] 就是销毁。
2. `session` / `module` 是"第一次用到时才建"，不是一开始就建 `session_flag` 的 `setup` 发生在 `test_c`（第一次有人要它），不是测试一开始
3. `teardown` 是逆序的。`setup` 顺序：`session_flag` → `module_client`；`teardown` 顺序：`module_client` → `session_flag`。 和 `with 嵌套`、装饰器包裹一个道理：后进先出。
4. 销毁的时机跟着 `scope` 走 `module_client` 在模块最后一条用例（test_d）结束后销毁；`session_flag` 等整轮结束。

### 3.3 `--setup-show` 的输出（贴一份）

**输出：**

```text
collected 4 items

week05/day30/scripts/test_03_scope.py::test_a
        SETUP    F shared_config
        week05/day30/scripts/test_03_scope.py::test_a (fixtures used: shared_config) PASSED
        TEARDOWN F shared_config
week05/day30/scripts/test_03_scope.py::test_b
        SETUP    F shared_config
        week05/day30/scripts/test_03_scope.py::test_b (fixtures used: shared_config) PASSED
        TEARDOWN F shared_config
week05/day30/scripts/test_03_scope.py::test_c
SETUP    S session_flag
    SETUP    M module_client
        week05/day30/scripts/test_03_scope.py::test_c (fixtures used: module_client, session_flag) PASSED
week05/day30/scripts/test_03_scope.py::test_d
        week05/day30/scripts/test_03_scope.py::test_d (fixtures used: module_client, session_flag) PASSED
    TEARDOWN M module_client
TEARDOWN S session_flag
```

### 3.4 什么时候必须每次新建（串味的例子）

| 这东西会被用例改吗？ | 该用什么 scope |
| --- | --- |
| 不会（只读配置、URL、只读常量） | session ✅ 放心共享 |
| 会被改，但改完要还原 | function（每条都干净） |
| 会被改，且不能还原（连接池、事务、临时文件） | function，或者自己写还原逻辑 |
| 建一次很贵、且只读 | session ✅ |

- 只读的共享，可写的每次新建

**串味例子：**

```py
@pytest.fixture(scope="session")      # ❌ 危险
def client():
    s = requests.Session()
    yield s
    s.close()

def test_a(client):
    client.headers["Authorization"] = "Bearer 过期token"   # 改了共享对象

def test_b(client):
    # 这里拿到的 client 已经带着 test_a 留下的脏 header
    assert "Authorization" not in client.headers          # ← 会失败，但不明显
```

## 四、autouse 和依赖链

### 4.1 `autouse=True` 的实测输出（注意顺序）

**输入：**

```py
import pytest

@pytest.fixture(autouse=True)
def auto_log():
    print("  [auto] 每个用例都自动跑我")
    yield
    print("  [auto] 收尾")


def test_x():          # ← 参数里没有 auto_log
    print("  [auto] 用例中")
    assert True
```

**输出：**

```text
collected 1 item

week05/day30/scripts/test_03b_autouse.py::test_x   [auto] 每个用例都自动跑我
  [auto] 用例中
PASSED  [auto] 收尾
```

**没有`autouse=True` 输出：**

```text
collected 1 item

week05/day30/scripts/test_03b_autouse.py::test_x   [auto] 用例中
PASSED
```

### 4.2 什么时候该用、什么时候别用

- 什么时候用：日志、清理残留文件、重置全局状态 —— 这些"每条用例都该做但没人想写参数"的事。
- 什么时候别用：autouse=True 用多了，测试会变得"看不出依赖" —— 新人读代码只知道"它用了 client"，不知道"它背后还偷偷连了数据库、还发了通知"。
- 如果 fixture 是"用例需要的数据"，就写参数；如果是"全局卫生"，才用 autouse

### 4.3 `client(cfg)` 这种依赖链怎么读

- `def client(cfg):` 括号里的 `cfg` **就是依赖声明** —— 不用在用例里写 `base_url`。

- `--setup-show` 会直接印出来：

```text
SETUP  S cfg
SETUP  S client (fixtures used: cfg)      ← 依赖关系写在这
```

## 五、改造 test_report.py

### 5.1 改的三处

| # | 改什么 | 为什么 |
| --- | --- | --- |
| ① | BASE_URL / TIMEOUT → cfg fixture | 换环境只改 fixture，不改用例 |
| ② | get(uid) → client fixture（requests.Session） | 连接复用（Day 28 实测 1.139s → 0.227s） |
| ③ | 用例里 r = get(...) → 参数声明 client, cfg | 用例只留"发请求 + 断言" |

### 5.2 改完的代码

**①：**

```py
@pytest.fixture(scope="session")
def cfg():
    return {"baseUrl": "https://httpbin.org", "timeout": 10, "endpoint": "/get"}
```

**②：**

```py
@pytest.fixture(scope="session")
def client(cfg):
    s = requests.Session()
    print("  [setup] Session 建好了")
    yield s
    s.close()
    print("  [teardown] Session 关掉了")
```

**③：**

```py
def test_user_1_ok(client, cfg):
    r = client.get(cfg["baseUrl"] + cfg["endpoint"],
                   params={"userId": "1"}, timeout=cfg["timeout"])
    assert r.status_code == 200
```

### 5.3 跑通输出（`[setup]` 只一次）

**输出：**

```text
collected 3 items

week05/day30/scripts/test_04_report_fixture.py::test_user_1_ok   [setup] Session 建好了
PASSED
week05/day30/scripts/test_04_report_fixture.py::test_user_2_ok PASSED
week05/day30/scripts/test_04_report_fixture.py::test_status_404 PASSED  [teardown] Session 关掉了
```

### 5.4 把 scope 改成 function 后的对比

**把 scope 改成 function 后的输出：**

```text
collected 3 items

week05/day30/scripts/test_04_report_fixture.py::test_user_1_ok   [setup] Session 建好了
PASSED  [teardown] Session 关掉了

week05/day30/scripts/test_04_report_fixture.py::test_user_2_ok   [setup] Session 建好了
PASSED  [teardown] Session 关掉了

week05/day30/scripts/test_04_report_fixture.py::test_status_404   [setup] Session 建好了
PASSED  [teardown] Session 关掉了
```

- 从全局只创建一次，变成每个用例创建一次

## 六、诊断

### 6.1 fixture 报错是 ERROR 还是 FAILED（贴两种）

**实验文件**：`scripts/demo_06_error.py`（**故意全是 ERROR**，用 demo_ 开头，
所以不进全量收集；要跑就显式指定路径）

**两种 ERROR：**

```text
EE                                                                       [100%]

=================================== ERRORS ====================================
_____________________ ERROR at setup of test_need_missing _____________________
file demo_06_error.py, line 6
  def test_need_missing(no_such_fixture):
E       fixture 'no_such_fixture' not found
>       available fixtures: broken, capfd, capfdbinary, caplog, capsys, ...
>       use 'pytest --fixtures [testpath]' for help on them.

______________________ ERROR at setup of test_use_broken ______________________

    @pytest.fixture
    def broken():
>       raise RuntimeError("配置读不到")
E       RuntimeError: 配置读不到

=========================== short test summary info ============================
ERROR demo_06_error.py::test_need_missing
ERROR demo_06_error.py::test_use_broken - RuntimeError: 配置读不到
2 errors in 0.21s
```

| 类型 | 报什么 | 排查方向 |
|---|---|---|
| 名字对不上 | `fixture 'xxx' not found` + available fixtures | 参数名写错，照列表改 |
| fixture 内部出错 | `ERROR at setup` + 你抛的异常 | 配置/连接/前置条件 |

**另外两种容易混的情况**：

| 现象 | 退出码 | 含义 |
|---|---|---|
| `FAILED` | 1 | 用例**跑了**，断言没过 |
| `ERROR at setup` | 1 | 用例**没跑起来**（fixture / 环境） |
| `ERROR: file or directory not found` | **4** | **命令本身打错了**，收集都没开始 |

### 6.2 `--fixtures` / `--setup-show` / `-s` 各看什么

- `--fixtures` ：看现在能用哪些 fixture
- `--setup-show` ：看清谁在什么时候建，又在什么时候拆
- `-s` ：看清断言里 `print` 的内容

## 七、自检 10 题

| # | 问题 | 一句话回答 |
| --- | --- | --- |
| 1 | fixture 是怎么被"调起来"的（谁看参数名、谁执行） | `fixture` 名 看参数名。同名的函数负责执行 |
| 2 | yield 之前 / 之后各是什么阶段 | `yield` 之前是用例之前，`yield` 之后是用例之后 |
| 3 | 用例失败时，yield 之后的代码还执行吗 | 执行，无论用例成不成功， `yield` 之后的代码都会执行 |
| 4 | function / module / session 各建几次、何时销毁 | `function`每条用例建一次，用例结束销毁。`module` 每个.py文件建一次，文件结束销毁。`session` 每次运行建一次，运行结束销毁。 |
| 5 | teardown 的顺序为什么是逆序 | 因为后建的需要先拆 |
| 6 | 哪些东西不能设成 session 作用域，为什么 | 会被改的不能设，因为会‘串味’ |
| 7 | autouse=True 的两个好处和一个坏处 | 可以清理残留文件，可以重置全局状态。但是用多了会导致看不出依赖 |
| 8 | fixture 依赖 fixture，靠什么声明 | 靠参数名声明。 def api(base_url): 就是说"我要 base_url"。 |
| 9 | 为什么 fixture 出错是 ERROR 不是 FAILED，排查方向差在哪 | ERROR = 用例**没跑起来**（setup 阶段失败）→ 查 fixture 名字 / fixture 内部异常 / 环境；FAILED = 用例**跑了**但断言没过 → 查被测系统行为 / 期望值。两者方向完全不同 |
| 10 | --setup-show 和 -s 各看什么 | `--setup-show` 看pytest 自己的 setup/teardown 顺序 + 依赖链 + 作用域标记。`-s` 看用例/fixture 里 print 的东西 |

## 八、还没搞懂的

- 无

## 九、今日 3 题

- Q053 | fixture 和普通函数的区别 | 用例写参数名声明需求，pytest 找同名 fixture 先执行再把返回值注入参数，不用显式调用 | 🔁
- Q054 | yield 版 fixture 的清理何时执行 | 用例结束后；scope 决定时机（module 在模块末、session 在整轮末），多个 fixture 逆序收尾 | 🔁
- Q055 | 什么情况不能把 fixture 设成 session 作用域 | 有状态或会被用例修改的东西；共享会串味，导致单跑绿、一起跑红 | 🔁

> **写完后跑** `python tools/sync_qa.py`
