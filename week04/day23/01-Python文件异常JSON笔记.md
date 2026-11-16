# Day 23 ｜ Python 回炉 ①：文件 / 异常 / JSON

## 一、文件

### 1.1 四种读法各用在哪（贴代码片段）

1. 全读成一个大字符串（适合小文件、JSON）

```py
with open("data/config.json", encoding="utf-8") as f:
    text = f.read()
```

2. 读成行列表（适合要按行处理）

```py
with open("data/users.csv", encoding="utf-8") as f:
    lines = f.readlines()      # 每行末尾带 \n
```

3. 逐行迭代（适合大文件，不占内存）

```py
with open("data/users.csv", encoding="utf-8") as f:
    for line in f:
        line = line.rstrip("\n")   # 去掉换行
```

4. 一次读一行（手动控制）

```py
with open("data/users.csv", encoding="utf-8") as f:
    while True:
        line = f.readline()
        if not line:
            break
```

### 1.2 编码三种报错：我亲手制造的三个

| # | 制造方法 | 报错/现象 | 学到什么 |
| --- | --- | --- | --- |
| ① | 写 utf-8，读不写 encoding | 'gbk' codec can't decode | 默认编码不可移植（Linux 上不报错） |
| ② | 写 gbk，读 utf-8 | 'utf-8' codec can't decode | 编码必须和文件真实编码一致 |
| ③ | 写 utf-8-sig，读 utf-8 | 开头多 \ufeff | BOM 是看不见的字符 |

**判据**：报错里是哪个 codec，就说明代码在用哪种编码读。

### 1.3 `newline="\n"` 的验证（xxd 输出）

`xxd week04/day23/data/demo.txt | head -3`输出：

```text
00000000: e7ac ace4 b880 e8a1 8cef bc9a e6b5 8be8  ................
00000010: af95 0ae7 acac e4ba 8ce8 a18c efbc 9ae6  ................
00000020: 8ea5 e58f a30a                           ......

```

## 二、异常

### 2.1 try/except/else/finally 各在什么时候跑

| 块 | 什么时候执行 |
| --- | --- |
| try | 无论如何 |
| except X | 只捕获 X 类型的异常 |
| else | 没有异常时（区别于"写在 try 末尾"） |
| finally | 无论如何（包括 return 之前） |

### 2.2 三种"不该捕获"的写法

| 写法 | 为什么错 |
| --- | --- |
| except: pass | 出错了当没发生，后面会报一个完全无关的错 |
| except Exception 包住一切 | 分不清是"文件没有"还是"格式坏了"，没法针对性处理 |
| try 里包了 20 行 | 你不知道哪行出错的 |

### 2.3 五个常见异常 + 怎么防

| 异常 | 什么时候 | 怎么防 |
| --- | --- | --- |
| FileNotFoundError | 路径写错 / 文件没生成 | os.path.exists() 先判 |
| json.JSONDecodeError | 文件不是合法 JSON | try 捕获，打印原始内容 |
| KeyError | d["token"] 但字段不存在 | 用 d.get("token") |
| ValueError | int("abc") | 先判类型或 try |
| requests.exceptions.Timeout | 接口超时 | 显式 timeout= + 捕获 |

### 2.4 自定义异常用在哪

- 自定义异常常用在让调用方能精确地区分"配置问题"和"网络问题"，从而给不同的处理的地方。

**例如：**

```py
class ConfigError(Exception):
    """配置不合法（不存在 / 格式错 / 缺字段）"""
    pass


def load_config(path):
    if not os.path.exists(path):
        raise ConfigError("配置文件不存在: %s" % path)

    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        # 把底层错误"包"成配置错误，同时保留原始异常链
        raise ConfigError("配置格式错误（第 %d 字符）：%s" % (e.pos, e.msg)) from e
```

### 2.5 制造三个错误

1. 文件不存在：

```py
try:
    open("week04/day23/data/not-here.json", encoding="utf-8")
except FileNotFoundError as e:
    print("① 捕获到：", type(e).__name__)
```

**输出：**

```text
① 捕获到： FileNotFoundError
```

2. JSON 坏了：

```py
try:
    json.loads('{"a": 1,, }')
except json.JSONDecodeError as e:
    print("② 捕获到：", type(e).__name__, "| 位置：", e.pos,"| 错误原因：", e.msg)
```

**输出：**

```text
② 捕获到： JSONDecodeError | 位置： 8 | 错误原因： Expecting property name enclosed in double quotes
```

3. 键不存在

```py
d = {"name": "张三"}
try:
    print(d["token"])
except KeyError as e:
    print("③ 捕获到：", type(e).__name__, "| 缺的键：", e)
```

**输出：**

```text
③ 捕获到： KeyError | 缺的键： 'token'
```

## 三、JSON

### 3.1 load / loads / dump / dumps 四个的区别

| 函数 | 输入 | 输出 | 什么时候用 |
| --- | --- | --- | --- |
| json.loads(s) | 字符串 | dict | 响应体 response.text |
| json.dumps(d) | dict | 字符串 | 打印、日志、拼请求体 |
| json.load(f) | 文件对象 | dict | 读配置文件 |
| json.dump(d, f) | dict + 文件对象 | 写入文件 | 存结果 |

- 带 s 的是 string（字符串），不带的是文件。
- **验证方法**：改 indent 后看 out.json 文件，别只看终端 —— `back == d` 永远是 True，因为它比的是数据不是格式。

### 3.2 ensure_ascii 前后对比

```py
import json
d = {"name": "张三"}
print(json.dumps(d))
print(json.dumps(d, ensure_ascii=False)) 
```

**ensure_ascii 前：**

```text
{"name": "\u5f20\u4e09"}
```

**ensure_ascii 后：**

```text
{"name": "张三"}
```

### 3.3 `[]` vs `.get()` 的选择依据

- 一定存在该字段的时候用 `[]`
- 不确定存不存在该字段的时候用 `.get()`

### 3.4 响应不是 JSON 时怎么防御

```py
def parse_json(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None       # 或抛出，但要让调用方知道

data = parse_json(response.text)
if data is None:
    print("[WARN] 响应不是 JSON，前 100 字符：%r" % response.text[:100])
```

### 3.5 JSON 存盘再读回

**输入：**

```text
见scripts/03_json_demo.py
```

**输出：**

```text
① 默认: {"name": "\u5f20\u4e09", "tags": ["qa", "api"], "nested": {"ok": true}}
② 中文: {"name": "张三", "tags": ["qa", "api"], "nested": {"ok": true}}
③ 缩进: {
  "name": "张三",
  "tags": [
    "qa",
    "api"
  ],
  "nested": {
    "ok": true
  }
}
④ 读回来一样吗: True
```

## 四、综合脚本

### 4.1 report.py 的结构（三段：读配置 / 跑用例 / 写结果）

**读配置：**

```py
def load_config(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)
```

**跑用例：**

```py
def run_case(cfg, row):
    url = cfg["baseUrl"] + cfg["endpoint"]
    r = requests.get(url, params={"userId": row["userId"]}, timeout=cfg["timeout"])
    return {
        "userId": row["userId"],
        "expected": int(row["expected"]),
        "actual": r.status_code,
        "pass": r.status_code == int(row["expected"]),
    }
```

**写结果：**

```py
def main():
    cfg = load_config(CONFIG)
    results = []
    with open(DATA, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            results.append(run_case(cfg, row))

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    passed = sum(1 for r in results if r["pass"])
    failed = len(results) - passed
    print("共 %d 条 | 通过 %d | 失败 %d" % (len(results), passed, failed))

    sys.exit(1 if failed else 0)
```

### 4.2 三种坏情况的真实输出

1. 配置不存在：

```bash
mv week04/day23/data/config.json week04/day23/data/config.json.bak
python week04/day23/scripts/report.py
mv week04/day23/data/config.json.bak week04/day23/data/config.json
```

**输出：**

```text
[FATAL] 配置文件不存在：week04/day23\data\config.json
```

2. JSON 坏了：

```bash
cp week04/day23/data/config.json week04/day23/data/config.json.bak
echo '{"baseUrl": "https://httpbin.org",,}' > week04/day23/data/config.json
python week04/day23/scripts/report.py
mv week04/day23/data/config.json.bak week04/day23/data/config.json
```

**输出：**

```text
[FATAL] JSON 格式错误（第 34 个字符）：Expecting property name enclosed in double quotes
```

3. 超时（把 timeout 改成 0.001）：

```bash
python -c "
import json
p='week04/day23/data/config.json'
d=json.load(open(p,encoding='utf-8')); d['timeout']=0.001
json.dump(d,open(p,'w',encoding='utf-8'),ensure_ascii=False,indent=2)"
python week04/day23/scripts/report.py
```

**输出：**

```text
共 3 条 | 通过 0 | 失败 3
```

### 4.3 退出码的用途

- CI 里判"这次跑没跑过"，看的就是退出码（0 成功、非 0 失败）。

## 五、自检 10 题

| # | 问题 | 能答出来吗 |
| --- | --- | --- |
| 1 | "w" 和 "a" 的区别，用错 "w" 会怎样 | "w"是覆盖，"a"是追加，用错"w"会导致原文件被清空 |
| 2 | 为什么每个 open 都要写 encoding="utf-8" | 为了保证编码正确 |
| 3 | UnicodeDecodeError 和乱码，分别说明什么 | UnicodeDecodeError 说明是系统自带的编码和文件使用的编码不一致，乱码说明编码不符但字节恰好合法 |
| 4 | except: pass 为什么最危险 | 捕获之后没有反馈，会导致不知道有没有错误，也不知道错在哪里 |
| 5 | else 块和"写在 try 末尾"的区别 | 写在 try 末尾如果发生错误会被 except 捕获到。写在 else 里则不会 |
| 6 | json.load 和 json.loads 差在哪 | json.loads 输入的是字符串， json.load 输入的是文件 |
| 7 | 什么时候用 .get() 而不是 [] | 在确定有该字段的时候使用 [] ，在不确定是否有该字段的时候使用 .get() |
| 8 | ensure_ascii=False 不写会怎样 | 不写中文会被转义 |
| 9 | 脚本的退出码给谁看，为什么要 sys.exit(1) | 脚本的退出码是给CI看的，要确认脚本是否成功运行 |
| 10 | 三行数据全绿，为什么不能说明接口没问题 | 有隐形错误，例如`https://httpbin.org`只验证格式，不验证内容 |

## 六、还没搞懂的

- 能照着骨架写出 report.py，但**从零搭还是卡**（下一步：三阶练习的第 3 阶）
- 健壮性改动是照着改的，**自己设计“该防哪些坏情况”还不熟**

## 七、今日 3 题

- Q032 | `os.path.join` 会检查或创建文件吗 | 不会，它只拼字符串；真正创建文件的是 open | 🔁 |
- Q033 | `def` 定义时函数体会执行吗 | 不会，只有被调用时才执行；形参在调用时才有值 | 🔁 |
- Q034 | 改了 indent，为什么 `back == d` 还是 True | indent 只改格式不改数据，== 比的是数据 | 🔁 |

> **写完后跑** `python tools/sync_qa.py`
