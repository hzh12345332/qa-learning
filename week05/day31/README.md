# Day 31 ｜ conftest.py 分层 + 配置注入

产出：

| 文件 | 内容 |
|---|---|
| `01-conftest笔记.md` | 笔记主体（306 行，八章） |
| `conftest.py` | 根：`cfg`（**读 `config.json`**）+ `client`（`yield`/`close`，session 级） |
| `scripts/test_01_needs_no_import.py` | **不 import 也能拿到 fixture**；另有 `assert cfg == on_disk` 验证配置真读文件 |
| `scripts/test_cfg_is_root.py` | 证明子目录的覆盖**不污染父目录** |
| `scripts/test_sibling_sub.py` | 证明**只往下、不往上传**（`fixture 'only_in_sub' not found`） |
| `scripts/test_02_assert_dims.py` | 加练：同一个响应的**五维断言** |
| `scripts/sub/conftest.py` | 同名 `cfg` 覆盖 → `example.com` |
| `scripts/sub/test_01.py` | 覆盖生效的证据 |
| `scripts/conftest.py` | 把 `only_in_sub` 提上一层后变绿（"往上提"的实操） |
| `handwrite/conftest.py` + `test_handwrite.py` | **30 分钟从零手写**（不看参考） |

**跑一遍**：

```bash
cd /d/work/qa-learning
python -m pytest week05/day31 -q
# 9 passed in 5.53s        退出码 0
```

## 今天搞清的八点

1. **`conftest.py` 是 pytest 自动加载的配置/夹具文件** —— 靠**目录树**加载，不用 import、也不能 import。
2. **四条硬规则**（全部自己实测）：
   - **往下传**：根 `conftest.py` 的 fixture，子目录能用
   - **不往上传**：子目录的 fixture，父目录用不了 → `fixture 'xxx' not found`
   - **就近覆盖**：同名 fixture，离测试文件近的赢
   - **出错退出码 4**：`ImportError while loading conftest`，**一条测试都跑不起来**
3. **配置注入**：`cfg` 从硬编码改成读 `config.json` —— **换环境只改数据文件，不改代码**（本周硬指标的第一步）。
4. **验证"真的在读文件"的正确写法**：`assert cfg == on_disk`（和磁盘内容对比），**不是**断言某个临时字段。
5. **路径陷阱**：`"week04/day23/data/config.json"` 这种相对路径按 **cwd** 解析，不按 `conftest.py` 的位置。
6. **优先级链**：模块内定义 > 就近 `conftest.py` > 上层 `conftest.py`。
7. **`conftest.py` 里 import 自己项目的模块会失败**（rootdir 不在 `sys.path`），三种解法：写进去 / `pytest.ini` 配 `pythonpath = .` / `sys.path.insert`。
8. **`assert 条件, 消息` 里消息是惰性求值** —— 条件为真时**根本不执行**，所以消息里的错字会一直藏着。

## 备注（今天的坑）

- **把测试函数写进了 `conftest.py`** → `collected 0 items`，**零报错**，但一条都没跑（`conftest.py` 只被加载、不被收集）
- **加练里写了 `r.test[:200]`**（应为 `r.text`）→ 因为断言消息惰性求值，**状态码 200 时永远不报错**；一旦失败会抛 `AttributeError` 把真实原因顶掉
- **改坏 `config.json` 做实验后忘了改回来** → `git status` 一直显示 `M`，靠它才发现
- **删掉实验字段 `marker` 后，依赖它的测试挂了** → 测试不该依赖脚手架；改成 `assert cfg == on_disk`
- **一开始把 `client` 的 scope 写成 `function`** → 连接复用全没了（Day 28 实测 1.139s → 0.227s），改回 `session`

## 30 分钟从零手写（周三惯例）

| 项 | 结果 |
|---|---|
| 用时 | **25 分钟** |
| 结果 | **3 passed** |
| 判据 | ✅ **第 3 阶过了**（30 分钟内写出能跑的 conftest + fixture + 用例） |
| 卡在哪 | `/status/404` 该不该用 `cfg["endpoint"]` |
| 对答案改的 | ① `client` 的 scope 改回 `session` ② 三条用例补 `timeout=cfg["timeout"]` |

**卡点的结论**：
- `/get` 是**配置里的 endpoint** → `cfg["baseUrl"] + cfg["endpoint"]`
- `/status/404` 是**这条用例专用路径**，配置里没有 → 直接拼
- 判据：**"这个路径会被别的用例复用吗？"** 会 → 进配置；只这一条用 → 写在测试里

## 加练（断言）

- 题目：**同一个响应，五个维度的断言**（状态码 / 顶层类型 / 必需字段 / 字段值 / 响应耗时）
- 结果：✅ 5 条全绿
- **顺带抓出一个隐性 bug**：`r.test[:200]` 拼错（应为 `r.text`）—— 因为断言消息**只在条件为假时才求值**，状态码正常时它永远不暴露。
  **危害**：哪天状态码不对，抛的是 `AttributeError: 'Response' object has no attribute 'test'`，真实原因被埋。

## 明天（11/26 周四）：`parametrize` 数据驱动

**今天把"配置"从代码里赶出去了。但"数据"还在代码里**：

```python
def test_user_1_ok(client, cfg):
    r = client.get(..., params={"userId": "1"}, ...)     # ← "1" 写死

def test_user_2_ok(client, cfg):
    r = client.get(..., params={"userId": "2"}, ...)     # ← "2" 也写死
```

| 今天 | 明天 |
|---|---|
| 一个用户一个函数 | **一个函数跑 N 组数据** |
| 数据写死在代码里 | 数据放进 `users.csv`（Day 23 那个） |
| 加用户要改代码 | **加一行 CSV 就行** ← 本周硬指标 |

> 今晚 3 分钟想一件事：`users.csv` 有 `userId` 和 `expected` 两列，
> **一次 `parametrize` 要把两列都传给用例，参数该怎么写？**
