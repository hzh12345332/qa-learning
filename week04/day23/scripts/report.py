import csv
import json
import os
import sys

import requests



BASE = "week04/day23"
CONFIG = os.path.join(BASE, "data", "config.json")
DATA = os.path.join(BASE, "data", "users.csv")
OUT = os.path.join(BASE, "data", "report.json")


def load_config(path):
    if not os.path.exists(path):
        raise SystemExit("[FATAL] 配置文件不存在：%s" % path)
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise SystemExit("[FATAL] JSON 格式错误（第 %d 个字符）：%s" % (e.pos, e.msg))

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

if __name__ == "__main__":
    main()