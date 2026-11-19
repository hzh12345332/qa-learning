# Day 26 ｜ 装饰器（下）：带参装饰器 / 写 3 个

产出：

| 文件 | 内容 |
|---|---|
| `01-装饰器下笔记.md` | 笔记主体（250 行，八章） |
| `scripts/01_decorator_with_args.py` | 三层结构演示（`times` 只打印，**不重试**——教学版） |
| `scripts/02_retry.py` | `@retry` 完整实现 + 3 次尝试成功 / 全失败抛出 |
| `scripts/03_log.py` | `@log_calls`：脱敏、截断、异常记完还抛 |
| `scripts/04_class_decorator.py` | 类装饰器：`__call__` + `update_wrapper`，能读 `calls` |
| `scripts/decorators.py` | **三个装饰器齐全**：`timer` / `log_calls` / `retry` |
| `scripts/report_class.py` | 抽出 `_do_request`（会抛），`@retry` 才真正生效 |
| `scripts/verify_retry.py` | 离线验证：monkeypatch `requests.get` 让它必定超时 |
| `data/report.json` | 3 条用例全 pass 的产物（不入库） |

## 今天搞清的八点

1. **带参装饰器是三层**：外层收参数 → 中层收函数 → 内层收调用参数。
   `@retry(times=3)` 等价于 `run_case = retry(times=3)(run_case)`。
2. **忘写括号不报错**（静默）：`times` 拿到的是函数、`func` 拿到的是调用实参；
   直到调用时才抛 `AttributeError: 'int' object has no attribute '__name__'` 或 `TypeError: 'function' object cannot be interpreted as an integer`。
3. **`times` 是"最多试几次"的上限**，不是"必须跑满"——成功一次立刻 `return`。
4. **`@retry` 只认"抛出来的异常"，不认返回值**。`return False` / `return None` 都不算失败。
   最后一次失败必须 `raise`，否则失败用例假装通过。
5. **边界模型**：装饰器只能看到"穿过它那条边界"的异常。
   所以 `@retry` 必须贴在**最内层会抛**的地方（`_do_request`），贴在吞异常的外层等于没有。
6. **`log_calls` 脱敏是三层分工**：`SENSITIVE`（打谁）+ `_safe_items`（逐个检查）+ `_mask`（怎么打）。
   业务代码自己也不准 print 密码——装饰器保护不了业务层的 print。
7. **类装饰器**：`__call__` 让实例能被调用，`update_wrapper` 是类版的 `@wraps`；
   类版的独特价值是**能读状态**（`do_work.calls`）。
8. **闭包靠"顺序"，类靠"名字"**：`__closure__[0]` 会随变量改名而变，`obj.calls` 不会。

## 备注（今天的坑）

- 从 `01_decorator_with_args.py` 借 `retry` → `TypeError: retry() got an unexpected keyword argument 'delay'`（那是教学版，签名只有 `times`）
- `def retry` 缩进进了 `class` 体 → 变成类属性，`decorators.py` 里反而没有它
- 忘了 `import time` → `delay > 0` 时才炸（潜伏 bug）
- `@retry` 加在 `run_case` 上完全没效果 → 因为 `run_case` 内部 `except Timeout` 把异常吃了；看 `[retry]` 行才发现
- 正常跑 `report_class.py` **本来就不会有 `[retry]` 行**（请求都成功），要看必须制造失败
- `awk` 列号依赖日志格式：`[16/Nov/2026]` → 状态码 `$8`；带时区 `+0800` → `$9`
- `${1-:access.log}` 少写一个冒号 → 默认值变成字面量 `":access.log"`，`awk` 打不开文件

## 加练（Shell）

- 题目：日志状态码统计（`练习/shell/2026-11-19-日志状态码.sh`）
- 结果：✅ `200 3` / `500 1` / `404 1`，与判据一致
- 卡在哪：**列号数错**（短日期格式状态码在 `$8`，不是手册默认的 `$9`）——学会先用
  `awk 'NR==1{for(i=1;i<=NF;i++) printf "第%d列 = [%s]\n", i, $i}'` 数字段再写 `$N`

## 明天

Day 27：生成器 / 迭代器 / 推导式

> 今天的 `@retry` 是"多次执行同一个函数"；明天的 `yield` 是"一个函数分多次返回"——
> 一个往外重复调用，一个往里分段产出，正好是一对。
