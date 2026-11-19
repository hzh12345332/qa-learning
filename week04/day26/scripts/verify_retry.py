import requests
import report_class as rc


def fake_get(*args, **kwargs):
    raise requests.exceptions.Timeout("被替换：必定超时")


requests.get = fake_get          # ← 全局替换


runner = rc.ReportRunner("x", "y", "report.json")
runner.cfg = {"baseUrl": "https://httpbin.org", "endpoint": "/get", "timeout": 5}
print(runner.run_case({"userId": "1", "expected": "200"}))