import csv
import json
import os
import sys
import logging
from decorators import timer, retry
from api_client import ApiClient

import requests

logger = logging.getLogger("qa.report")

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
        logger.info("配置加载完成：%s", self.cfg["baseUrl"])


    @retry(times=3, delay=0.2,
           exceptions=(requests.exceptions.Timeout,
                       requests.exceptions.ConnectionError))
    def _do_request(self, client, path, uid):
        """只负责发请求，异常原样抛出"""
        return client.get(path, userId=uid)

    def run_case(self, client, row):
        try:
            r = self._do_request(client, self.cfg["endpoint"], row["userId"])
            actual, error = r.status_code, None
        except requests.exceptions.Timeout:
            actual = None
            error = "timeout"
        except requests.exceptions.RequestException as e:
            actual, error = None, type(e).__name__

        expected = int(row["expected"])
        ok = actual == expected
        logger.info("userId=%s expected=%s actual=%s → %s",
                    row["userId"], expected, actual, "PASS" if ok else "FAIL")
        return {
            "userId": row["userId"], "expected": expected, "actual": actual,
            "pass": actual == expected, "error": error,
        }

    @timer
    def run_all(self):
        self.load_config()
        with ApiClient(self.cfg["baseUrl"]) as client:
            with open(self.data_path, encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    self.results.append(self.run_case(client, row))

    def write_report(self):
        out_dir = os.path.dirname(self.out_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(self.out_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        logger.info("报告已写入：%s", self.out_path)

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
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,          # ← 加这个，日志进 stdout
    )
    src = "week04/day23"          # 输入：复用昨天的数据
    dst = "week04/day28"          # 输出：写进今天自己的目录
    runner = ReportRunner(
        os.path.join(src, "data", "config.json"),
        os.path.join(src, "data", "users.csv"),
        os.path.join(dst, "data", "report.json"),
    )
    sys.exit(1 if runner.run() else 0)


if __name__ == "__main__":
    main()