# Day 28 ｜ 上下文管理器 / requests 封装 / logging

产出：

| 文件 | 内容 |
|---|---|
| `01-上下文管理器&logging笔记.md` | 笔记主体（289 行，七章） |
| `scripts/01_context_basic.py` | `Timer` 类（`__enter__`/`__exit__`）+ 吞/不吞异常对照 |
| `scripts/02_contextmanager.py` | `@contextmanager` 版（`yield` 前是 enter、后是 exit） |
| `scripts/api_client.py` | **正式版 `ApiClient`**：`Session` + 统一 baseUrl/timeout/token |
| `scripts/03_api_client.py` | 只验证，不重复定义（`from api_client import ApiClient`） |
| `scripts/04_logging_basic.py` | `basicConfig` 三行上手 |
| `scripts/05_logging_handlers.py` | `getLogger` + 控制台/文件双 handler |
| `scripts/06_logging_pitfalls.py` | **三个日志坑的复现**（`python 06_logging_pitfalls.py 1/2/3`） |
| `scripts/decorators.py` | `timer` / `log_calls` / `retry`（Day 26 的成果） |
| `scripts/report_class.py` | **三块整合**：`with ApiClient` + `logger` + 保留全部健壮性 |
| `data/report.json` | 3 条用例全 pass 的产物（不入库） |

## 今天搞清的七点

1. **`with` 背后只有两个方法**：`__enter__` 进、`__exit__` 出。
   **`__exit__` 返回 `True` 会吞异常**，返回 `False`/`None` 才继续抛 —— 默认永远写 `False`。
2. **`@contextmanager` 就是 `try/finally + yield`**：`yield` 之前是 `__enter__`，之后是 `__exit__`。
   **必须用 `try/finally` 包住 `yield`**，否则代码块抛异常时清理不执行。
3. **装饰器管“函数”，上下文管理器管“代码块”**：想量 `main()` 里某三行用 `with`，想长期盯 `run_case` 用装饰器。
4. **`Session` 复用连接 + 统一 headers**；`requests.get` 每次新建 —— 批量请求必须用 `Session`。
5. **Client 层抛异常、用例层接住转结果**：Client 只负责“如实报告”，用例层负责“翻译成 `pass: False` + `error`”。
   **Client 层吞异常 → `@retry` 永远不生效**（Day 26 的坑）。
6. **`basicConfig` 只生效第一次**，项目里要用 `getLogger(__name__)` + handler；
   **配置权集中在入口，使用权分散到各模块**。
7. **`log.info("x=%s", v)` 不要用 `%` 拼**：被过滤掉的日志不该做字符串拼接。

## 备注（今天的坑）

- **`if __name__ == "__main__": main()` 忘写** → 定义了 `main()` 但从不调用 → **零输出零报错**
- **整段复制参考骨架** → 丢了自己的健壮性代码；`dst` 写回 `week04/day26`（应 day28）
- **备了零件没装**：`from api_client import ApiClient` 导入了但没用；`logger` 定义了但从没调用
- **两份 `ApiClient`**：`03_api_client.py` 里的原件没删，和 `api_client.py` 重复 → 改一个忘一个
- **`_do_request` 上留了 `@log_calls`** → 输出多出 `[call] args=(<ApiClient object>...)`，而且它没脱敏、绕过日志级别
- **`log_calls` 的 `print` 走 stdout，`logger` 走 stderr** → 两个流混着看，顺序显得乱
- **`basicConfig` 默认写 stderr**：`python x.py > out.txt` 抓不到日志，要用 `2>`
- **日志文件不关会锁住**：`FileHandler` 不 `close()`，Windows 上删不掉（`PermissionError`）

## 加练（断言）

- 题目：同一条断言三种写法（`expect` / `jsonBody` / `jsonSchema`）
- 结果：✅ **5/5 PASSED**（原 2 条 + 新 3 条）
- 卡在哪：
  1. **`jsonSchema` 只写了 `token`，漏了 `authenticated`** → 另一个字段类型错了也不报警
  2. **缺一个逗号** → `SyntaxError: Unexpected identifier 'token'`，**脚本根本没执行**（不是断言失败）

## 明天（11/22 周日）：复盘 + 重写

**不学新东西，做两件事**：

1. **从零重写 `report.py`**（函数版，限时 40 分钟，不看参考）—— `PLAN.md` 里的「待复习」
2. 写 `week04/周复盘/2026-11-16至11-22.md`

> 今天的 `ApiClient` 就是第 5 周框架 `api/` 层的雏形；
> 今天把“发请求 / 记日志 / 关资源”都封好了，明天重写时会轻松很多。
