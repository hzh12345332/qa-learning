import time
import requests
from functools import wraps

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            print("[timer] %s %.3fs" % (func.__name__, time.perf_counter() - start))
    return wrapper

def retry(times=3, delay=0.0, exceptions=(Exception,)):
    """失败后重试，最后一次失败原样抛出"""
    def deco(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(times):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if i == times - 1:        # 最后一次：不再重试
                        raise                 # ← 原样抛出
                    print("[retry] 第 %d 次失败：%s" % (i + 1, type(e).__name__))
                    if delay:
                        time.sleep(delay)
        return wrapper
    return deco

class ApiClient:
    """一个最小的接口客户端：统一 baseUrl / token / timeout"""

    def __init__(self, base_url, token=None, timeout=10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        if token:
            self.session.headers["Authorization"] = "Bearer %s" % token

    def _url(self, path):
        return self.base_url + "/" + path.lstrip("/")

    @retry(times=3, delay=0.5,
           exceptions=(requests.exceptions.Timeout,
                       requests.exceptions.ConnectionError))
    @timer
    def get(self, path, **params):
        return self.session.get(self._url(path), params=params, timeout=self.timeout)

    @timer
    def post(self, path, json=None, **params):
        return self.session.post(self._url(path), json=json,
                                 params=params, timeout=self.timeout)

    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()               # ← 无论怎么退出都关
        return False               # ← 不吞异常

if __name__ == "__main__":
    with ApiClient("https://httpbin.org/", token="token") as client:
        print("① URL 拼接:", client._url("/get"))                  # 看有没有 //
        print("② Authorization:", client.session.headers.get("Authorization"))
        r1 = client.get("/get", userId=1)
        r2 = client.get("/get", userId=2)                          # 两次 → 两条 [timer]

