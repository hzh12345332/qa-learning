import csv
import json
import os
import requests


BASE   = "week04/day23"                              # 数据还用昨天的，别复制
CONFIG = os.path.join(BASE, "data", "config.json")
DATA   = os.path.join(BASE, "data", "users.csv")
OUT    = os.path.join("week05/day29", "data", "report_b0.json")                          # 输出写到 week05/day29/data/

def load_config(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def run_case(cfg, row):
    url = cfg["baseUrl"] + cfg["endpoint"]
    r = requests.get(url, params={"userId": row["userId"]}, timeout=cfg["timeout"])
    expected = int(row["expected"])
    return {
        "userId": row["userId"],
        "expected": expected,
        "actual": r.status_code,
        "pass": r.status_code == expected,
    }

def main():
    cfg = load_config(CONFIG)
    results = []
    with open(DATA, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            results.append(run_case(cfg, row))
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    passed = sum(1 for it in results if it["pass"])
    print("共 %d 条 | 通过 %d | 失败 %d" % (len(results), passed, len(results) - passed))
    return 0 if passed == len(results) else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())