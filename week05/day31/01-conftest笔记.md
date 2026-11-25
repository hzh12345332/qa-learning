# Day 31 ｜ conftest.py 分层 + 配置注入

## 一、conftest.py 是什么

### 1.1 从"每个文件一份 fixture"到"放一次处处用"（贴两版对比）

**每个文件一份：**

```py
@pytest.fixture(scope="function")
def cfg():
    return {"baseUrl": "https://httpbin.org", "timeout": 10, "endpoint": "/get"}


@pytest.fixture(scope="function")
def client(cfg):
    s = requests.Session()
    yield s
    s.close()
```

**放一次处处用：**

```py
@pytest.fixture(scope="session")
def cfg():
    return {"baseUrl": "https://httpbin.org", "timeout": 10, "endpoint": "/get"}


@pytest.fixture(scope="session")
def client(cfg):
    s = requests.Session()
    yield s
    s.close()
```

### 1.2 为什么不用 import 就能用

- pytest 自动发现并加载了 conftest.py，不用经过任何 import 语句。

### 1.3 它的位置决定谁能用

```text
week05/
├── conftest.py                  ← 放这里：week05 下所有测试都能用
└── day31/
    ├── conftest.py              ← 放这里：只有 day31 下的能用
    └── scripts/
        └── test_xxx.py
```

## 二、四条硬规则（每条贴我自己的实测）

### 2.1 往下传：根 conftest 的 fixture，子目录能用

```text
probe_conf/
├── conftest.py          ← 定义 root_cfg
├── test_root.py         ← 用 root_cfg  ✅
└── sub/
    ├── conftest.py      ← 定义 sub_cfg
    └── test_sub.py      ← 既用 sub_cfg，也用 root_cfg  ✅
```

### 2.2 不往上传：子目录的 fixture，根目录用不了

```text
probe_conf/test_bad.py::test_root_use_sub_cfg

E       fixture 'sub_cfg' not found
>       available fixtures: ... root_cfg, shared, ...        ← 只有根的，没有 sub_cfg
```

- fixture 只往下传，不往上传。

### 2.3 就近覆盖：同名 fixture 谁赢

```text
sub/test_sub.py::test_sub_use_shared    [setup] shared（子目录覆盖了根的同名 fixture）
    >> test_sub_use_shared -> from-sub          ← 子目录的赢了

test_root.py::test_root_use_shared      [setup] shared（根 conftest）
    >> test_root_use_shared -> from-root        ← 根目录的测试还是用根的
```

### 2.4 出错退出码 4，一条都不跑

```text
# conftest.py
import not_exist_module_xyz
ImportError while loading conftest 'probe_conf/sub/conftest.py'.
conftest.py:1: in <module>
    import not_exist_module_xyz
E   ModuleNotFoundError: No module named 'not_exist_module_xyz'
```

## 三、配置注入

### 3.1 昨天的 cfg 硬编码在哪

- 昨天的 cfg 硬编码在代码里

```py
def load_config(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)
```

### 3.2 改成读 config.json（贴代码）

```py
import json
import os

import pytest
import requests

# 数据还在 day23（别复制，直接读）
CONFIG_PATH = "week04/day23/data/config.json"


def load_config(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def cfg():
    """配置 → 从 config.json 读，不再硬编码"""
    return load_config(CONFIG_PATH)


@pytest.fixture(scope="session")
def client(cfg):
    s = requests.Session()
    yield s
    s.close()
```

### 3.3 路径陷阱：相对路径按 cwd 算

- `CONFIG_PATH = "week04/day23/data/config.json"` 是相对路径
- 相对路径约定从仓库根跑
- 想按 conftest.py 的位置往上算：

```py
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_PATH = os.path.join(ROOT, "week04", "day23", "data", "config.json")
```

### 3.4 验证：改坏 config.json → 用例失败（贴输出）

**`config.json`改为：**

```js
{
    "baseUrl": "https://httpbin.o",
    "timeout": 10,
    "endpoint": "/get"
}
```

**输出：**

```text
E   socket.gaierror: [Errno 11001] getaddrinfo failed

The above exception was the direct cause of the following exception:
E   urllib3.exceptions.NameResolutionError: HTTPSConnection(host='httpbin.rog', port=443): Failed to resolve 'httpbin.rog' ([Errno 11001] getaddrinfo failed)

The above exception was the direct cause of the following exception:
E   urllib3.exceptions.MaxRetryError: HTTPSConnectionPool(host='httpbin.rog', port=443): Max retries exceeded with url: /get?userId=1 (Caused by NameResolutionError("HTTPSConnection(host='httpbin.rog', port=443): Failed to resolve 'httpbin.rog' ([Errno 11001] getaddrinfo failed)"))

During handling of the above exception, another exception occurred:
E   requests.exceptions.ConnectionError: HTTPSConnectionPool(host='httpbin.rog', port=443): Max retries exceeded with url: /get?userId=1 (Caused by NameResolutionError("HTTPSConnection(host='httpbin.rog', port=443): Failed to resolve 'httpbin.rog' ([Errno 11001] getaddrinfo failed)"))
D:\Python312\Lib\site-packages\requests\adapters.py:729: requests.exceptions.ConnectionError: HTTPSConnectionPool(host='httpbin.rog', port=443): Max retries exceeded with url: /get?userId=1 (Caused by NameResolutionError("HTTPSConnection(host='httpbin.rog', port=443): Failed to resolve 'httpbin.rog' ([Errno 11001] getaddrinfo failed)"))
============================================================================================ short test summary info ============================================================================================
FAILED week05/day31/scripts/test_01_needs_no_import.py::test_user_1_ok - requests.exceptions.ConnectionError: HTTPSConnectionPool(host='httpbin.rog', port=443): Max retries exceeded with url: /get?userId=1 (Caused by NameResolutionError("HTTPSConnection(host='httpbin.rog', port...
1 failed, 1 passed in 0.35s
```

**把 config.json 的 baseUrl 改成不存在的域名 `httpbin.rog` 后：**

- `test_user_1_ok` 报 `ConnectionError`（DNS 解析失败）→ **证明 cfg 真的在读文件**（不是缓存/硬编码）
- 注意：这是**异常**（请求没发出去），不是**断言失败**
- `test_cfg_came_from_file` **仍然通过** —— 因为它只断言 `cfg["baseUrl"]` 非空，没真的发请求

## 四、分层

### 4.1 什么时候才需要多个 conftest

| 场景 | 例子 |
| --- | --- |
| 不同测试目录要不同的前置条件 | scripts/ 用 httpbin；以后 testcases/ 用你项目 1 的接口 |
| 某个目录要覆盖一个全局 fixture | 根上 cfg 读 config.json；某个目录的 cfg 读另一份配置 |

### 4.2 我做的覆盖实验（贴 sub/ 和 scripts/ 的两种输出）

| 层级 | 谁定义 | 优先级 | 用途 |
| --- | --- | --- | --- |
| 模块内 | test_04_report_fixture.py | 最高 | 只给本文件用 |
| 就近 conftest | day31/conftest.py、scripts/sub/conftest.py | 中 | 一组测试共用 |
| 上层 conftest | week05/conftest.py | 最低 | 全项目共用 |

**sub输出：**

```text
collected 1 item

week05/day31/scripts/sub/test_01.py::test_cfg {'baseUrl': 'https://example.com'}
PASSED
```

**scripts输出：**

```text
week05/day31/scripts/test_cfg_is_root.py::test_cfg_is_root   scripts/ 拿到的 cfg = {'baseUrl': 'https://httpbin.org', 'timeout': 10, 'endpoint': '/get', 'marker': 'changed-by-me'}
```

> `marker` 是我为验证"配置真的从文件读"临时加的字段，验完已删除。

### 4.3 三个坑

- 坑一：以为"子目录的 fixture 根目录也能用"
- 坑二：conftest.py 里 import 自己的模块失败
- 坑三：多个 conftest.py 里出现同名 fixture，却忘了谁覆盖谁

### 4.4 分层实验：四次对照（今天的核心证据）

同一套测试，只改 `conftest.py` 的位置，看 `cfg` / `only_in_sub` 的变化：

| # | 测试在哪 | fixture 定义在哪 | 结果 | 证明了什么 |
|---|---|---|---|---|
| 1 | `scripts/sub/` | `sub/conftest.py` | `{'baseUrl': 'https://example.com'}` | 子目录的 `cfg` **覆盖**了根的 |
| 2 | `scripts/` | `day31/conftest.py` | `https://httpbin.org` | 覆盖**不污染父目录** |
| 3 | `scripts/` | `sub/conftest.py`（子目录独有） | **`fixture 'only_in_sub' not found`** | **只往下，不往上传** |
| 4 | `scripts/` | `scripts/conftest.py`（提上一层） | PASSED | 往上提一层就生效 |

**第 3 条的报错原文**：

（贴 `fixture 'only_in_sub' not found` + available fixtures 那几行）

**结论一句话**：
**fixture 的可见范围 = 定义它的 conftest.py 所在目录「往下」的整棵子树。**

### 4.5 day31 文件清单（每个文件演示一件事）

| 文件 | 演示什么 | 跑法 |
|---|---|---|
| `day31/conftest.py` | 根 fixture：`cfg`（读 config.json）+ `client`（yield/close） | 被下面所有测试用 |
| `scripts/test_01_needs_no_import.py` | 不 import 也能拿到 fixture | `pytest scripts` |
| `scripts/test_cfg_is_root.py` | 根的 `cfg` 没被子目录污染 | `pytest scripts` |
| `scripts/sub/conftest.py` | 同名 `cfg` 覆盖 → example.com | — |
| `scripts/sub/test_01.py` | 覆盖生效的证据 | `pytest scripts/sub -s` |
| `scripts/test_sibling_sub.py` | **可见范围：只往下不往上** | 见文件头注释 |
| `scripts/conftest.py` | 把 `only_in_sub` 提上一层后变绿 | — |

**一句话**：`sub/` 是"子目录覆盖"的实验，`test_sibling_sub.py` 是"可见范围"的实验。

## 五、30 分钟从零手写

### 5.1 成绩：25 分钟，3 passed

### 5.2 卡在哪

卡在"`/status/404` 该不该用 `cfg["endpoint"]`"。

想清楚了：

- **`/get` 是配置里的 endpoint** → 用 `cfg["baseUrl"] + cfg["endpoint"]`
- **`/status/404` 是"这条用例专用的路径"** → 配置里没有它，**直接拼死在测试里**

判据：**"这个路径会被别的用例复用吗？"** 会 → 进配置；只这一条用 → 写在测试里。

### 5.3 对完答案，我改了哪几处

1. **`client` 的 scope：我写了 `function`，答案用 `session`** → 改回 `session`
   - 原因：`Session` 的价值就是连接复用，`function` 等于每条用例重建一次（Day 28 实测 1.139s → 0.227s）
2. **给三条用例补 `timeout=cfg["timeout"]`**（原来没写，网络卡住会挂死）

## 六、自检 10 题

| # | 问题 | 一句话回答 |
| --- | --- | --- |
| 1 | conftest.py 为什么不用 import 就能用 | 因为 pytest 会自动加载 |
| 2 | 根 conftest.py 的 fixture 能被子目录用吗？反过来呢？ | 根目录可以被子目录用。反过来不可用 |
| 3 | 两个 conftest.py 有同名 fixture，谁赢 | 离测试文件近的那个赢 |
| 4 | conftest.py 出错时退出码是几，影响范围多大 | 退出码是4，会导致一条用例都跑不了 |
| 5 | 为什么不建议 from conftest import xxx | pytest 会自己加载，再 import 一次容易出问题 |
| 6 | cfg 读文件后，换环境要改哪个文件 | 改 cfg 读的那个文件 |
| 7 | 相对路径 week04/... 是相对谁解析的 | 相对路径按 cwd 算 |
| 8 | conftest.py 里 import 自己的模块为什么可能失败，三种解法 | 为什么失败：pytest 的 rootdir（比如 D:\work\qa-learning）不在 sys.path 里。import 只认 sys.path 上的目录，所以 from utils.helper import load_config 找不到。解法：① 函数直接写在 conftest.py 里；② pytest.ini 加一行；③ conftest.py 顶部 sys.path.insert(0, ROOT) |
| 9 | 分层的两个正当用途 | 不同测试目录要不同的前置条件、某个目录要覆盖一个全局 fixture |
| 10 | --fixtures 怎么帮你排查"这个 fixture 哪来的" | 按当前目录列出所有可用的 fixture（含来源），一眼看出 cfg 是哪个文件给的。 |

## 七、还没搞懂的

- 无

## 八、今日 3 题

- Q056 | conftest.py 是干什么的，为什么不用 import | pytest 自动加载的配置/夹具文件，放 fixture；同目录及子目录的测试自动可用，靠目录树加载而不是 import | 🔁
- Q057 | 多个 conftest.py 的 fixture 谁覆盖谁 | 就近优先（子目录覆盖父目录）；fixture 只向下生效，父目录用不了子目录的 | 🔁
- Q058 | conftest.py 出错会怎样 | 加载期报 ImportError，退出码 4，整轮一条测试都跑不起来 | 🔁

> **写完后跑** `python tools/sync_qa.py`
