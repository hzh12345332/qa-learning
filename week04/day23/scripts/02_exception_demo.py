import json

# ① 文件不存在
try:
    open("week04/day23/data/not-here.json", encoding="utf-8")
except FileNotFoundError as e:
    print("① 捕获到：", type(e).__name__)

# ② JSON 坏了
try:
    json.loads('{"a": 1,, }')
except json.JSONDecodeError as e:
    print("② 捕获到：", type(e).__name__, "| 位置：", e.pos,"| 错误原因：", e.msg)

# ③ 键不存在
d = {"name": "张三"}
try:
    print(d["token"])
except KeyError as e:
    print("③ 捕获到：", type(e).__name__, "| 缺的键：", e)