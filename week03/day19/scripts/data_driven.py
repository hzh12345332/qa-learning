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