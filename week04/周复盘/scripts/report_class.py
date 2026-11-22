import csv
import json
import os
import requests
import sys
from collections import Counter

BASE = "week04/day23"
OUTPUT = "week04/周复盘"
CONFIG = os.path.join(BASE, "data", "config.json")
DATA = os.path.join(BASE, "data", "users.csv")
OUT = os.path.join(OUTPUT, "data", "report.json")

def load_config(path):
    "给一个路径，把那个 JSON 文件打开、读出来、变成字典、关掉文件、把字典还给你。"
    if not os.path.exists(path):    # exists读取磁盘，(path)是已经保存好的join文件。os.path.extsts(path)就是读取磁盘里是否存在path的内容
        raise FileNotFoundError("[FATAL] 配置文件不存在：%s" % path)    # if not 就会抛出FileNotFoundError
    try:
        with open(path, encoding="utf-8") as f:     # 用utf-8打开path
            return json.load(f)     # 输入文件对象f，返回dict字典
    except json.JSONDecodeError as e:       # 如果 json.load(f) 因为 JSON 格式不对而抛出这个异常，就抓住它，并给它起名叫 e
        raise SystemExit("[FATAL] JSON 格式错误（第 %d 行第 %d 列）：%s" % (e.lineno, e.colno, e.msg))

def run_case(cfg, row):
    url = cfg["baseUrl"] + cfg["endpoint"]
    try:
        r = requests.get(url, params={"userId": row["userId"]}, timeout=cfg["timeout"])
        actual = r.status_code
        error = None
    except requests.exceptions.Timeout:
        actual = None
        error = "timeout"
    except requests.exceptions.RequestException as e:
        actual = None
        error = type(e).__name__
    expected = int(row["expected"])
    return {
    "userId": row["userId"], "expected": expected, "actual": actual,
    "pass": actual == expected, "error": error,
}

def summary(results):
    print("按状态码统计：")
    for code, n in Counter(item["actual"] for item in results).most_common():
        print("  %s: %d 条" % (code if code is not None else "未拿到响应", n))

def main():
    uid = sys.argv[1] if len(sys.argv) > 1 else None
    cfg = load_config(CONFIG)
    results = []
    with open(DATA, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if uid and row["userId"] != uid:               # ← 新增 2 行
                continue
            results.append(run_case(cfg, row))
        if not results:
            print("[WARN] 没有匹配的用例:userId=%s" % uid)
            return 2    

        with open(OUT, "w", encoding="utf-8", newline="\n") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

    passed = sum(1 for item in results if item["pass"])
    failed = sum(1 for item in results if not item["pass"])
    summary(results)
    print("共 %d 条 | 通过 %d | 失败 %d" % (len(results), passed, failed))
    return 1 if failed else 0



if __name__ == "__main__":
    sys.exit(main())