# Day 28 ｜ 上下文管理器 / requests 封装 / logging

## 一、上下文管理器

### 1.1 `with` 背后的两个方法（`__enter__` / `__exit__`）

| 方法 | 什么时候调 | 干什么 | 返回什么 |
| --- | --- | --- | --- |
| `__enter__` | 进 with 时 | 准备资源 | 给 as 后面的变量 |
| `__exit__` | 无论怎么退出 都调 | 释放资源 | True = 吞掉异常，False/None = 继续抛 |

### 1.2 我写的 `Timer` 类（贴代码 + 输出）

**输入：**

```py
import time


class Timer:
    """用 with 计时一个代码块"""

    def __init__(self, name="代码块"):
        self.name = name

    def __enter__(self):
        self.start = time.perf_counter()
        print("[进入] 开始计时：", self.name)
        return self                 # ← 给 as 后面的变量（这里用不上，但要有）

    def __exit__(self, exc_type, exc_val, exc_tb):
        cost = time.perf_counter() - self.start
        print("[退出] %s 耗时 %.3fs" % (self.name, cost))
        return False                # ← False = 不吞异常


with Timer("读文件"):
    time.sleep(0.1)
```

**输出：**

```text
[进入] 开始计时： 读文件
[退出] 读文件 耗时 0.100s
```

### 1.3 `__exit__` 返回 True 和 False 的差别（贴两次输出）

**`__exit__` 返回 True的输出：**

```text
=== 返回 True(吞)===
  __exit__ 收到异常： ValueError
  程序还在跑（异常被吞）
```

**`__exit__` 返回False的输出：**

```text
=== 返回 False(不吞)===
  __exit__ 收到异常： ValueError
  外面抓到了： 炸了
```

### 1.4 `@contextmanager` 版，和类版差多少行

| 区别 | 类版 | @contextmanager 版 |
| --- | --- | --- |
| 要写什么 | `__enter__` + `__exit__` | 一个 yield |
| 代码量 | 15 行 | 8 行 |
| `__exit__` 能不能返回 True 吞异常 | ✅ 能 | ⚠️ 要 try/except 包住 yield 才行 |
| 适合 | 复杂资源、要存状态 | 简单场景（90% 的情况） |

### 1.5 三种释放资源写法，我以后选哪个

| 写法 | 代码 | 什么时候用 |
| --- | --- | --- |
| ① try/finally | f = open(...) / try: ... / finally: f.close() | 学习原理；极简场景 |
| ② 类 + `__enter__`/`__exit__` | 自己写个类 | 资源复杂、要带状态、要吞异常 |
| ③ @contextmanager | 一个 yield 函数 | 推荐，简单场景首选 |

- 我以后选择③ @contextmanager
- 适用场景广，使用简单

## 二、requests 封装

### 2.1 不封装时的五个问题

| 问题 | 后果 |
| --- | --- |
| 每次调用都新建连接 | 慢（没复用 TCP） |
| timeout 每处都要记得传 | 漏一个就可能永久挂住 |
| token/headers 每处都要拼 | 改一次要改几十处 |
| 出错处理各写一遍 | 有的抛、有的返回 None、有的返回 "timeout" |
| 想统计"总共发了几个请求" | 做不到 |

### 2.2 Session 和 requests.get 的区别

| 区别 | requests.get(...) | Session.get(...) |
| --- | --- | --- |
| 连接 | 每次新建 | 复用 |
| headers | 每次单独传 | session.headers 统一 |
| cookies | 不自动保存 | 自动保存和带上 |
| 适合 | 一次性脚本 | 一个项目/一套用例 |

### 2.3 我的 ApiClient（贴代码）

- 正式版在 `api_client.py`，核心三块：

```py
class ApiClient:
    def __init__(self, base_url, token=None, timeout=10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        if token:
            self.session.headers["Authorization"] = "Bearer %s" % token

    def _url(self, path):
        return self.base_url + "/" + path.lstrip("/")
```

### 2.4 错误处理：Client 层抛、用例层接，为什么这么分

| 层 | 策略 |
| --- | --- |
| Client 层（发请求） | 让异常抛 —— 它只负责"如实报告发生了什么" |
| 用例层（run_case） | 接住异常，转成 {"pass": False, "error": "timeout"} |

- @retry 只能抓抛出来的异常（昨天踩过的坑）。Client 层把异常吃掉，重试就永远不会生效。
- Client 层负责“如实报告”（成功返回，失败抛出）； 用例层负责“翻译成结果”（pass: False + error）； 谁都不许把失败伪装成成功。

### 2.5 `with ApiClient(...)` 出来的效果

**输出：**

```text
① URL 拼接: https://httpbin.org/get
② Authorization: Bearer t
[timer] get 1.305s
[timer] get 0.241s
```

## 三、logging

### 3.1 print 的五个问题

| 问题 | print | logging |
| --- | --- | --- |
| 能不能分级 | ❌ | ✅ DEBUG/INFO/WARNING/ERROR |
| 能不能一键关掉 | ❌（要删代码） | ✅ level=WARNING |
| 能不能同时写文件 | ❌ | ✅ 加个 handler |
| 有没有时间/来源 | ❌（要自己拼） | ✅ %(asctime)s %(name)s |
| 测试里想静音 | 做不到 | ✅ 一行配置 |

### 3.2 五个级别分别用在哪

| 级别 | 数值 | 用在哪 | 生产环境开吗 |
| --- | --- | --- | --- |
| DEBUG | 10 | 变量值、请求体、每一步细节 | ❌ |
| INFO | 20 | 正常流程（开始/结束/条数） | ✅ |
| WARNING | 30 | 可疑但不影响结果（配置缺失、重试了一次） | ✅ |
| ERROR | 40 | 这次失败了，但程序还能继续 | ✅ |
| CRITICAL | 50 | 整个程序不能继续 | ✅ |

### 3.3 `basicConfig` vs `getLogger + handler`

| 区别 | basicConfig() | getLogger(name) |
| --- | --- | --- |
| 配置的是谁 | root logger（全局唯一） | 你指定名字的那个 |
| 能调用几次 | 只有第一次有效 | 随时 |
| 影响范围 | 整个进程 | 只管这个名字（和子 logger） |
| 日志里的 %(name)s | 永远叫 root | 模块名（`__name__`） |

### 3.4 `log.info("x=%s", v)` 为什么不用 `%` 拼

| 写法 | 什么时候做字符串拼接 |
| --- | --- |
| log.info("x=%s" % v) | 无论如何都拼（即使这条日志被过滤掉） |
| log.info("x=%s", v) | 只有真要输出时才拼 ✅ |

### 3.5 我踩的坑（重复输出/不生效）

**不生效输入：**

```py
import logging, sys
FMT = "[%(levelname)s] %(name)s: %(message)s"

logging.basicConfig(level=logging.DEBUG, format=FMT, stream=sys.stdout)
logging.debug("1) 第一次配 DEBUG → 能出来")

logging.basicConfig(level=logging.WARNING, format=FMT, stream=sys.stdout)
logging.debug("2) 本该消失，但还在出")
logging.info("3) INFO 也在出 → level 还是 DEBUG(10)")
```

**不生效输出：**

```text
[DEBUG] root: 1) 第一次配 DEBUG → 能出来
[DEBUG] root: 2) 本该消失，但还在出 → 第二次没生效
[INFO] root: 3) INFO 也在出 → level 还是 DEBUG(10)
```

**重复输出输入：**

见 `06_logging_pitfalls.py` 的实验 2 / 3：

```bash
python 06_logging_pitfalls.py 2     # root 多挂一个 handler
python 06_logging_pitfalls.py 3     # propagate=True 冒泡
```

**重复输出：**

```text
qa.propagate = True
[qa][INFO] 这条出现两次：自己的 handler 一次 + 冒泡到 root 一次
[qa][INFO] 这条出现两次：自己的 handler 一次 + 冒泡到 root 一次
```

## 四、整合进 report_class

### 4.1 改的三处

1. `_do_request` 加参数 `client` ，把 `requests.get` 改为 `client.get`
2. `run_case` 加参数 `client`
3. `run_all` 增加  `with ApiClient`

### 4.2 跑通输出

```text
2026-11-21 22:20:08,762 [INFO] qa.report: 配置加载完成：https://httpbin.org
[timer] get 3.561s
2026-11-21 22:20:12,315 [INFO] qa.report: userId=1 expected=200 actual=200 → PASS
[timer] get 0.245s
2026-11-21 22:20:12,557 [INFO] qa.report: userId=2 expected=200 actual=200 → PASS
[timer] get 0.243s
2026-11-21 22:20:12,812 [INFO] qa.report: userId=999 expected=200 actual=200 → PASS
[timer] run_all 4.052s
2026-11-21 22:20:12,812 [INFO] qa.report: 报告已写入：week04/day28\data\report.json
共 3 条 | 通过 3 | 失败 0
```

### 4.3 和 26 号的输出对比

**day26输出：**

```text
[call] _do_request args=(<__main__.ReportRunner object at 0x0000015F536BF860>, 'https://httpbin.org/get', '1') kwargs={}
[timer] _do_request 1.936s
[call] _do_request args=(<__main__.ReportRunner object at 0x0000015F536BF860>, 'https://httpbin.org/get', '2') kwargs={}
[timer] _do_request 2.688s
[call] _do_request args=(<__main__.ReportRunner object at 0x0000015F536BF860>, 'https://httpbin.org/get', '999') kwargs={}
[timer] _do_request 1.097s
[timer] run_all 5.721s
共 3 条 | 通过 3 | 失败 0
```

## 五、自检 10 题

| # | 问题 | 一句话回答 |
| --- | --- | --- |
| 1 | with 背后调了哪两个方法 | `__enter__`和`__exit__` |
| 2 | `__exit__` 返回 True 会发生什么 | 异常被吞 |
| 3 | @contextmanager 和 yield 的关系 |  @contextmanager 就是"try/finally + yield"打包成的装饰器 |
| 4 | 装饰器和上下文管理器各管什么 | 装饰器管"函数"，上下文管理器管"代码块" |
| 5 | Session 比 requests.get 好在哪（说两条） | 可以复用；session.headers 统一 |
| 6 | 为什么 Client 层要让异常抛出去 | 因为用例层需要根据异常输出，如果不抛就会导致假全绿 |
| 7 | logging 的五个级别，什么时候用 WARNING | `DEBUG`;`INFO`;`WARNING`;`ERROR`;`CRITICAL`。可疑但不影响结果时用 `WARNING` |
| 8 | basicConfig 为什么有时不生效 | 已经被调用过一次，第二次调用就不会生效 |
| 9 | 日志重复打印两次，可能是什么原因 | ① addHandler 两次 ② propagate=True 冒泡到 root |
| 10 | log.info("x=%s" % v) 和 log.info("x=%s", v) 差什么 | `log.info("x=%s" % v)` 无论如何都拼；`log.info("x=%s", v)` 只有需要输出的时候才拼 |

## 六、还没搞懂的

- 无

## 七、今日 3 题

- Q047 | `with` 背后的两个方法 | `__enter__` 进入返回资源，`__exit__` 退出（正常/异常都调） | 🔁
- Q048 | `@contextmanager` 怎么实现的 | 用生成器：yield 之前是 enter，之后是 exit，要 try/finally | 🔁
- Q049 | 为什么用 logging 不用 print | 能分级、能按级别关、能同时写文件、自带时间和来源 | 🔁

> **写完后跑** `python tools/sync_qa.py`

- 加练：断言三种写法，卡在：`jsonSchema` 只写了 token，漏了 authenticated；缺一个逗号导致脚本根本没执行
