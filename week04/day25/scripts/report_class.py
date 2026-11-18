import csv
import json
import os
import sys

from decorators import timer, log_calls

import requests

class ReportRunner:
    def __init__(self,config_path, data_path,out_path):
        self.config_path = config_path
        self.data_path = data_path
        self.out_path = out_path
        self.cfg = None
        self.results = []

    def load_config(self):
        if not os.path.exists(self.config_path):
            raise SystemExit("[FATAL] 配置文件不存在：%s" % self.config_path)
        try:
            with open(self.config_path, encoding="utf-8") as f:
                self.cfg = json.load(f)
        except json.JSONDecodeError as e:
            raise SystemExit("[FATAL] JSON 格式错误（第 %d 个字符）：%s" % (e.pos, e.msg))

    @timer
    @log_calls
    def run_case(self, row):
        url = self.cfg["baseUrl"] + self.cfg["endpoint"]
        try:
            r = requests.get(url, params={"userId": row["userId"]}, timeout=self.cfg["timeout"])
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

    @timer
    def run_all(self):
        self.load_config()
        with open(self.data_path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                self.results.append(self.run_case(row))

    def write_report(self):
        out_dir = os.path.dirname(self.out_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(self.out_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

    def summary(self):
        passed = sum(1 for r in self.results if r["pass"])
        failed = len(self.results) - passed
        return "共 %d 条 | 通过 %d | 失败 %d" % (len(self.results), passed, failed)

    def run(self):
        self.run_all()
        self.write_report()
        print(self.summary())
        failed = sum(1 for r in self.results if not r["pass"])
        return failed

def main():
    src = "week04/day23"          # 输入：复用昨天的数据
    dst = "week04/day25"          # 输出：写进今天自己的目录
    runner = ReportRunner(
        os.path.join(src, "data", "config.json"),
        os.path.join(src, "data", "users.csv"),
        os.path.join(dst, "data", "report.json"),
    )
    sys.exit(1 if runner.run() else 0)

if __name__ == "__main__":
    main()