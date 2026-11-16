import json

d = {"name": "张三", "tags": ["qa", "api"], "nested": {"ok": True}}

print("① 默认:", json.dumps(d))
print("② 中文:", json.dumps(d, ensure_ascii=False))
print("③ 缩进:", json.dumps(d, ensure_ascii=False, indent=2))

with open("week04/day23/data/out.json", "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=2)

with open("week04/day23/data/out.json", encoding="utf-8") as f:
    back = json.load(f)
print("④ 读回来一样吗:", back == d)