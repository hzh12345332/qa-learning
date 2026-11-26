# Day 32 ｜ parametrize：users.csv 接入 + ids

## 一、parametrize 基本形态

### 1.1 一个函数跑三组（贴代码 + `-v` 输出）

**输入：**

```py
import pytest

@pytest.mark.parametrize("uid", ["1", "2", "999"])
def test_uid(uid):
    assert uid.isdigit()
```

```bash
python -m pytest week05/day32/scripts/test_01_first_parametrize.py -v
```

**输出：**

```text
collected 3 items

week05/day32/scripts/test_01_first_parametrize.py::test_uid[1] PASSED                        [ 33%]
week05/day32/scripts/test_01_first_parametrize.py::test_uid[2] PASSED                        [ 66%]
week05/day32/scripts/test_01_first_parametrize.py::test_uid[999] PASSED                      [100%]

```

### 1.2 三要素：参数名 / 数据组 / 函数签名

| 要素 | 位置 | 作用 |
| --- | --- | --- |
| 参数名 | "uid" | 参数名（字符串；多个用逗号分隔） |
| 数据组 | ["1", "2", "999"] | 数据组：列表里每一项就是"一次运行用的值" |
| 函数签名 | def test_uid(uid) | 函数参数必须同名，pytest 按名字注入 |

### 1.3 用例名的生成规则（单值、多列、ids）

| 装饰器 | 函数（关键！） | 生成的用例名 |
| --- | --- | --- |
| @parametrize("uid", ["1","2"]) | def test_uid(uid) | test_uid[1]、test_uid[2] |
| @parametrize("a,b", [(1,200),(2,404)]) | def test_no_ids(a, b) | test_no_ids[1-200]、test_no_ids[2-404] |
| @parametrize("x, y", [(1,1)]) | def test_with_space(x, y) | test_with_space[1-1] |

## 二、失败时它多给了什么

### 2.1 故意让一组失败（贴完整报告）

**输入：**

```py
@pytest.mark.parametrize("a,b", [(1, 200), (2, 404)])
def test_no_ids(a, b):
    assert b == 200
```

**输出：**

```text
a = 2, b = 404

    @pytest.mark.parametrize("a,b", [(1, 200), (2, 404)])
    def test_no_ids(a, b):
>       assert b == 200
E       assert 404 == 200

week05\day32\scripts\test_01_first_parametrize.py:9: AssertionError
```

> 演示完之后我用 `pytest.mark.xfail` 标记了这一组，
> 全量跑不再红；要看真实失败报告就加 `--runxfail`。

### 2.2 `a = 2, b = 404` 这一行是哪来的

- 是`parametrize("a,b", [(1, 200), (2, 404)])`来的
- `parametrize("a,b", [(1, 200), (2, 404)])`拆出两组数据，分别是：`a = 1, b = 200`和`a = 2, b = 404`

### 2.3 和"两个手写函数"的对比

| 手写函数 | `parametrize` |
| --- | --- |
| 一个用户一个函数 | 一个函数跑 N 组数据 |
| 数据写死在代码里 | 数据读 users.csv |
| 加用户要改代码 | 加一行 CSV 就多一条用例 |

## 三、一次传多列

### 3.1 `"userId,expected"` 怎么拆包

- 按照`,`进行拆包

| 参数名写法 | 每组数据要长什么样 | 函数签名 |
| --- | --- | --- |
| "uid" | "1"（单值） | def test_x(uid) |
| "a,b" | (1, 200)（两元组） | def test_x(a, b) |
| "a,b,c" | (1, 200, "ok") | def test_x(a, b, c) |

### 3.2 接真实接口的代码

**输入：**

```py
import pytest

CASES = [("1", 200), ("2", 200), ("999", 200)]


@pytest.mark.parametrize("userId,expected", CASES)
def test_user_get(client, cfg, userId, expected):
    r = client.get(cfg["baseUrl"] + cfg["endpoint"],
                   params={"userId": userId},
                   timeout=cfg["timeout"])
    assert r.status_code == expected, "userId=%s 返回 %s" % (userId, r.status_code)
```

### 3.3 类型陷阱：CSV 读出来是字符串（贴"全部失败"的输出）

**把`r.status_code == expected`改成`r.status_code == "200"`的输出：**

```text
week05/day32/scripts/test_02_two_cols.py::test_user_get[1-200] FAILED                                                                                                                                      [ 33%]
week05/day32/scripts/test_02_two_cols.py::test_user_get[2-200] FAILED                                                                                                                                      [ 66%]
week05/day32/scripts/test_02_two_cols.py::test_user_get[999-200] FAILED                                                                                                                                    [100%]
```

- 把`r.status_code == "200"`改成`r.status_code == 200`（去掉双引号）。程序可以正常运行，但是属于用人工分辨出类型，不如`r.status_code == expected`直接方便

### 3.4 分组失败的定位

- 把 ("999", 404) 写进去（期望 404，但 httpbin 返回 200）

**输出：**

```text
>       assert r.status_code == expected, "userId=%s 返回 %s" % (userId, r.status_code)
E       AssertionError: userId=999 返回 200
E       assert 200 == 404
E        +  where 200 = <Response [200]>.status_code

week05\day32\scripts\test_02_two_cols.py:11: AssertionError
============================================================================================ short test summary info ============================================================================================
FAILED week05/day32/scripts/test_02_two_cols.py::test_user_get[999-404] - AssertionError: userId=999 返回 200
```

| 信息 | 从哪来 |
| --- | --- |
| 哪一组挂了 | 用例名 [999-404] |
| 这组的值是什么 | userId = '999', expected = 404 |
| 我怎么写的诊断消息 | "userId=999 返回 200" |

### 3.5 同一个规则的两个面孔

Day 31 实验：`scripts/` 用不到 `scripts/sub/conftest.py` 的 fixture → **不往上传**
Day 32 实战：`day32/` 用不到 `day31/conftest.py` 的 fixture → **兄弟不可见**

统一成一句：**fixture 的可见范围 = conftest.py 所在目录「往下」的整棵子树。**
解决方式也一样：**把 conftest.py 往上提，直到它覆盖所有要用它的测试。**

## 四、从 users.csv 读数据

### 4.1 `load_cases()` 的写法

**输入：**

```py
import csv

import pytest

DATA = "week04/day23/data/users.csv"


def load_cases():
    """从 CSV 读 → [(userId, expected), ...]"""
    with open(DATA, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return [(r["userId"], int(r["expected"])) for r in rows]


CASES = load_cases()


@pytest.mark.parametrize("userId,expected", CASES)
def test_user_get(client, cfg, userId, expected):
    r = client.get(cfg["baseUrl"] + cfg["endpoint"],
                   params={"userId": userId},
                   timeout=cfg["timeout"])
    assert r.status_code == expected, "userId=%s 返回 %s" % (userId, r.status_code)
```

### 4.2 硬指标验收：加一行 CSV → 用例 +1（贴前后输出）

**加之前输出：**

```text
collected 3 items

week05/day32/scripts/test_03_from_csv.py::test_user_get[1-200] PASSED                                                                                                                                      [ 33%]
week05/day32/scripts/test_03_from_csv.py::test_user_get[2-200] PASSED                                                                                                                                      [ 66%]
week05/day32/scripts/test_03_from_csv.py::test_user_get[999-200] PASSED      
```

**加一行"3,200"之后输出：**

```text
collected 4 items

week05/day32/scripts/test_03_from_csv.py::test_user_get[1-200] PASSED                                                                                                                                      [ 25%]
week05/day32/scripts/test_03_from_csv.py::test_user_get[2-200] PASSED                                                                                                                                      [ 50%]
week05/day32/scripts/test_03_from_csv.py::test_user_get[999-200] PASSED                                                                                                                                    [ 75%]
week05/day32/scripts/test_03_from_csv.py::test_user_get[3-200] PASSED   
```

> `3,200` 这一行是为了验证硬指标加的，现在留着当第四条用例。

### 4.3 为什么不能放到用例里读

- parametrize 的第二个参数在「收集期」就必须算出值 —— 因为 pytest 要先知道"有几组数据"才能创建用例。 放在用例函数里读是运行时，那时候用例早就创建完了，来不及。

## 五、ids 与空列表

### 5.1 加 `ids` 前后用例名的对比

- 加 `ids` 前用例名：`test_user_get[1-200]`
- 加 `ids` 后用例名：`test_user_get[1]` / `[2]` / `[999]` / `[3]`

### 5.2 空列表 → 全 SKIPPED（贴输出）

**输出：**

```text
week05/day32/scripts/test_03_from_csv.py::test_empty[NOTSET] SKIPPED (got empty parameter set for (z)) 
```

### 5.3 为什么这比报错更危险，怎么防

- 为什么危险：如果 users.csv 读失败（路径错、文件空），load_cases() 返回 [] → 所有用例变 SKIPPED → 退出码 0 → CI 显示绿色。"什么都没测"被当成了"全过"。
- 怎么防：在 `load_cases` 加一句 `assert rows, "users.csv 里没有数据（路径错了？文件空了？）"`

## 六、自检 10 题

| # | 问题 | 一句话回答 |
| --- | --- | --- |
| 1 | `parametrize` 的三要素分别是什么 | 参数名，数据组，函数签名 |
| 2 | `parametrize("a,b", [(1,200)])` 里那个字符串的作用 | 拆包说明：告诉 pytest 每组数据按顺序拆给哪几个参数名  |
| 3 | 用例名里 [1-200] 的 - 是什么 | 多列用 - 拼 |
| 4 | 失败时 a = 2, b = 404 那一行是谁打的 | 是 `parametrize` 打的。失败时自动把这一组的所有参数值打出来。 |
| 5 | 为什么 load_cases() 必须在模块顶层调用 | parametrize 的第二个参数是收集期就要算出来的，不能放到用例里 |
| 6 | `expected` 从 CSV 读出来是什么类型，为什么必须转 | `expected` 从 CSV 里读出来是 `string` 类型。因为不转会导致 `string` == `int` 永为假。从而使用例一直失败 |
| 7 | ids= 解决什么问题 | 解决了当参数变复杂时还能通过用例名想起它在测什么 |
| 8 | 空数据列表会怎样，为什么危险，怎么防 | 如果 users.csv 读失败（路径错、文件空），load_cases() 返回 [] → 所有用例变 SKIPPED → 退出码 0 → CI 显示绿色。使用 `assert rows, "users.csv 里没有数据（路径错了？文件空了？）"` 进行防御 |
| 9 | 参数名和 fixture 名撞车会怎样 | parametrize 静默覆盖同名 fixture，不报错 —— 所以更危险（看不出值哪来的）。 会报 SyntaxError 的是另一种：def test_x(client, client)（函数参数重名）。 |
| 10 | 本周硬指标是哪一句，今天怎么证明它 | 加一行 CSV → 用例数 +1。见§4.2 |

## 七、还没搞懂的

- 无

## 八、今日 3 题

- Q059 | parametrize 的三个要素 | 参数名字符串（"a,b"）+ 数据组列表（每组一个元组）+ 函数签名同名收参数 | 🔁
- Q060 | ids 是干什么的，不写会怎样 | 自定义用例名让失败定位更清楚；不写就自动用参数值拼成 [1-200] | 🔁
- Q061 | parametrize 传空列表会怎样，为什么危险 | 每条都 SKIPPED（got empty parameter set），不是通过；数据读空时 CI 会误判为绿 | 🔁

## 九、今日加练

- Shell 参数组统计：`grep -oE` 提取用例名 → `sed` 去掉 `::` 和 `[...]` → `sort | uniq -c` 计数
- 卡在两个地方：
  1. **`[^]]` 这个写法**（取反集合里第一个 `]` 是字面量）→ 后来用 `[^ ]*`（避开空格）绕过去，好懂多了
  2. **`[ "total" -eq 0 ]` 少了 `$`** → 报 `total: integer expected`，因为 `"total"` 是字面字符串，不是变量
- 判据：总组数为 0 时 `exit 1`（"没跑"不能算成功），两个分支都验过

> **写完后跑** `python tools/sync_qa.py`
> **体检**：VS Code `Ctrl+Shift+B` → 「体检笔记：当前文件（自动找手册）」，红项改完再提交
