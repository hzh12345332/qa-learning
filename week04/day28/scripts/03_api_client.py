# 03_api_client.py —— 只验证，不重复定义
import sys

from api_client import ApiClient

if __name__ == "__main__":
    with ApiClient("https://httpbin.org/", token="t") as client:
        print("① URL 拼接:", client._url("/get"))
        print("② Authorization:", client.session.headers.get("Authorization"))
        r1 = client.get("/get", userId=1)
        r2 = client.get("/get", userId=2)
        print(r1.status_code, r2.status_code)