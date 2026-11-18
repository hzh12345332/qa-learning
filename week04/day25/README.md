# Day 25 ｜ 装饰器（上）：函数是一等公民 / 闭包

产出：

| 文件 | 内容 |
|---|---|
| `01-装饰器上笔记.md` | 笔记主体（490 行，七章） |
| `scripts/01_first_class.py` | 函数是一等公民：赋值 / 传参 / 返回 / 容器 |
| `scripts/02_closure.py` | 闭包：`__closure__` / `cell_contents` / late binding |
| `scripts/03_timer_manual.py` | 手工套壳 `run_case = timer(run_case)` |
| `scripts/03_timer.py` | 四段对照：手工 / 无 wraps / 有 wraps / 异常 |
| `scripts/decorators.py` | **第一个可复用模块**：`@timer` + `@log_calls` |
| `scripts/report_class.py` | B4：方法体没改，加了 `@timer`×2 + `@log_calls` |
| `data/report.json` | 3 条用例全 pass 的产物（不入库） |

## 今天搞清的六点

1. **`def` 只是赋值语句**，函数本身是个值：能赋给变量、当参数、当返回值、放容器。
   `run_case` 是函数，`run_case()` 是它的返回值 —— **加不加括号是两个世界**。
2. **闭包的三个条件**：有内层函数、内层引用外层变量、外层返回内层函数。
   它绑定的是**变量（cell）**，不是值 —— `__closure__[0].cell_contents` 能看到格子里装了什么。
3. **`@timer` 就是 `run_case = timer(run_case)`**（无括号一层，`@retry(3)` 是两层）。
   装饰器在**被装饰函数定义完的那一刻**执行，但**函数体要等调用**才跑。
4. **`*args, **kwargs` 让装饰器对签名透明**，`@wraps` 保住 `__name__` / `__doc__` / 签名。
   少了前者：包不了带参函数；少了后者：pytest 用例名全变 `wrapper`。
5. **late binding**：循环里建闭包共用一个 cell，调用时取"那一刻"的值，所以全是最后一个。
   三种修法里**只有工厂函数是真闭包**，默认参数和 `partial` 都是"当场存值"。
6. **`start` 必须在 wrapper 内部**。放外面时的误差 = 装饰时刻到调用时刻的间隔，
   所以小脚本里看不出来，import 场景下会变成几分钟。

## 备注（今天的坑）

- 笔记里把 `a = run_case` 写成"拿到返回值" → `is` 判断反了（`a = run_case` 是 `True`）
- `@wraps` 忘写 → `__name__` 变 `wrapper`，报告里分不清哪条用例失败
- `start` 放外面 → 连续调用耗时累加（`0.113 / 0.213 / 0.314 / 0.414 / 0.515`）
- `def wrapper(row, retry=1)` 把参数名写死 → 调用方传的 `retry=5` 被悄悄换成 1
- `time.time()` 分辨率约 1ms，而 `summary()` 只花约 1µs → 显示 `0.000`（**不是 bug**）
- 输出路径照抄 Day 24 的 `base`，产物写回了 `day23/data/` → 改成 `src` / `dst` 分离

## 加练（断言）

- 题目：给 `08-模拟 500` 补 L1/L2/L3 三层断言
- 结果：⬜ 跳过，**11/19 早上补**（不欠账，但要在进度表留痕）

## 明天

Day 26：装饰器（下）—— 带参数装饰器（`@retry(times=3)`）+ 写 3 个

> `decorators.py` 是第 5 周框架 `utils/` 的雏形：明天往里加 `@retry`，那才是它真正开始有"工具库"的样子。
