# Day 19 ｜ Runner 与 Mock

## 一、Runner 基础

### 1.1 三个入口（截图或描述版本）

| 位置 | 怎么进 |
| --- | --- |
| Collection 名字右边 ... | 菜单里找 Run collection |
| 顶部工具栏 | 有 Runner 图标 |
| 左侧 My Workspace 底部 | 有一个 Runner 入口 |

### 1.2 我第一次跑全集合的结果（贴汇总数字）

```text
Iterations    1
All tests     14        ← 所有断言的执行总次数
Errors        0
Duration      3s 19ms
Avg Resp Time 291 ms
```

### 1.3 Runner vs 手动 Send 的区别

| 角度 | 手动点 Send | Runner |
| --- | --- | --- |
| 速度 | 一条一条 | 一次跑完 |
| 顺序 | 你自己决定 | 按集合顺序 |
| 结果 | 看一眼就没了 | 出报告，能保存 |
| 数据 | 一次一组 | 一次 N 组 |

## 二、数据驱动

### 2.1 users.csv 的 4 行数据

```text
userId,expected
1,200
2,200
999,404
abc,400

```

### 2.2 我的 data_driven.py（贴脚本）

```python
import csv
import requests

CSV = "week03/day18/data/users.csv"
URL = "https://httpbin.org/get"

with open(CSV, encoding="utf-8") as f:
    for row in csv.DictReader(f):
        uid = row["userId"]
        expected = int(row["expected"])
        r = requests.get(URL, params={"userId": uid}, timeout=10)
        ok = r.status_code == expected
        print("%-6s -> %d (期望 %d) %s" % (uid, r.status_code, expected, "PASS" if ok else "FAIL"))
```

### 2.3 4 行数据的运行结果（为什么有两行 FAIL）

```text
1      -> 200 (期望 200) PASS
2      -> 200 (期望 200) PASS
999    -> 200 (期望 404) FAIL
abc    -> 200 (期望 400) FAIL
```

- httpbin 的 /get 根本不校验 userId
- 任何值都返回 200 + 原样回显

### 2.4 数据驱动的三个坑（BOM / 表头 / int）

| 坑 | 后果 |
| --- | --- |
| CSV 表头拼错 | row["userId"] 抛 KeyError |
| CSV 有 BOM（Excel 保存） | 表头变成 \ufeffuserId，同样 KeyError |
| 忘了 int() | "200" == 200 永远 False |

## 三、运行报告

### 3.1 三层定位：请求名 / 断言名 / 错误详情

| 层 | 例子 | 告诉你什么 |
| --- | --- | --- |
| 请求名 | 02-测试 GET 带 token | 哪条 |
| 断言名 | 状态码符合预期 | 哪一步 |
| 错误详情 | expected 200 to equal 400 | 为什么 |

### 3.2 怎么留证据（导出要付费）

- 汇总数字手抄：Iterations 1 / All tests 14 / Passed 14 / Failed 0
- 想看响应详情：在结果里点某条 → 跳到编辑界面 → Send 一次

### 3.3 三种"假通过"

| 情况 | 为什么假 |
| --- | --- |
| 断言只写状态码 | 字段全空也 PASS |
| 数据文件为空 | 0 轮迭代 = 0 个断言 = 全绿 |
| 请求被跳过 | 没跑当然不失败 |

## 四、模拟异常

### 4.1 为什么异常场景必须测

| 情况 | 真实发生频率 |
| --- | --- |
| 服务器 500 | 每天都有 |
| 接口 404（改路径 / 下线） | 每周都有 |
| 响应慢 / 超时 | 弱网、大查询时 |

- Mock 的目的是：控制返回，让这些场景“随时能复现”。

### 4.2 我的 08/09/10 三条请求（贴配置 + 断言）

**08配置**

```text
GET https://httpbin.org/status/500
```

**08断言**

```bash
pm.test("服务端错误返回 500", function () {
    pm.response.to.have.status(500);
});
```

**09配置**

```text
GET https://httpbin.org/status/404
```

**09断言**

```bash
pm.test("资源不存在返回 404", function () {
    pm.response.to.have.status(404);
});
```

**10配置**

```text
GET https://httpbin.org/delay/3
```

**10断言**

```bash
pm.test("延迟接口最终返回 200", function () {
    pm.response.to.have.status(200);
});
```

### 4.3 三个异常端点的输出

**08输出**

```text
passed 服务端错误返回 500
```

**09输出**

```text
passed 资源不存在返回 404
```

**10输出**

```text
passed 延迟接口最终返回 200
```

### 4.4 500 时前端该怎样、不该怎样

- **应该**：友好错误页，提示"服务异常，请稍后重试"
- **不应该**：白屏、显示堆栈、把后端报错原文给用户

## 五、冒烟测试

### 5.1 什么是冒烟测试

- Smoke Test = 只测"核心流程能不能走通"，不测细节。

### 5.2 我的微型冒烟（05 → 06 两条）

**步骤**

```text
1. Runner 里选 Day17 练习
2. 取消勾选 其他请求，只留 05 和 06
3. Run
```

**输出**

```text
All：2 ；Passed：2 ；Failed：0
```

- 说明："取 uuid → 传 uuid" 这条链路是通的。

### 5.3 冒烟测试的三个要求

| 要求 | 为什么 |
| --- | --- |
| 快（< 2 分钟） | 每次提交都要跑 |
| 只跑核心路径 | 全量回归留给完整集合 |
| 失败要能一眼定位 | 名字 + 断言名要清楚 |

## 六、自检 10 题

| # | 问题 | 一句话回答 |
| --- | --- | --- |
| 1 | Runner 和手动点 Send 有什么区别 | Runner是自动化的开始，多条断言可以一键运行 |
| 2 | CSV 里有几行数据，脚本跑几次？由什么决定 | CSV 有几行（不含表头），for row in csv.DictReader(f) 就循环几次。 |
| 3 | 数据驱动时，脚本怎么拿到当前这一行的数据 | ☐ |
| 4 | CSV 读出来的值为什么不能直接比较 | CSV读出来的是字符串，不能和数值进行直接比较 |
| 5 | 一份"能看的报告"需要哪三层信息 | 请求名、断言名、错误详情 |
| 6 | 三种"假通过"分别是什么 | 断言只写状态码、数据文件为空、请求被跳过 |
| 7 | 用 httpbin 造异常时，你控制的到底是什么 | 控制“服务器返回什么状态码、多久返回” |
| 8 | /status/500 和 /delay/3 各模拟什么场景 | /status/500模拟服务端错误返回；/delay/3模拟接口延迟 |
| 9 | 冒烟测试和全量回归的区别 | 冒烟测试只测核心链路是否正常运行，全量回归要考虑所有涉及到的模块 |
| 10 | 冒烟测试的三个要求 | 快、只跑核心链路、失败要可以一眼定位 |

## 七、还没搞懂的

- 数据驱动时，脚本怎么拿到当前这一行的数据

## 八、今日 2 题

- Q023 | pip install 报 "No matching distribution (from versions: none)" 怎么排查 | 先确认 pip 与 python 是否同一环境（改用 python -m pip），再换镜像源 | 🔁
- Q024 | 题 A（SQL）为什么错 | 先定主表再贴表，聚合里不能塞子查询，分组要带主键 | 🔁 | §九

> 已跑 `python tools/sync_qa.py` 并入题库（Q023–Q024）

## 九、周三手写（11/11）

- 选的是：题 A（SQL）

**卡在哪：**（7 个错，各对应一个知识点）：

| 错误 | 对应知识点 |
| --- | --- |
| SUM(子查询) | 聚合函数只能作用在列上 |
| LEFT JOIN 方向 | “全都要保留”的表放左边 |
| o.id = u.id | 关联键要找 xxx_id 那种字段 |
| WHERE COALESCE | 取值 vs 过滤，位置不同 |
| GROUP BY ... DESC | GROUP BY 不排序 |
| 缺 ORDER BY | 题目要求要逐条对应 |
| 1055 | GROUP BY 要含所有非聚合列 |

- 一次写对了吗：没有
