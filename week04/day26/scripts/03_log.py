import time
from functools import wraps

SENSITIVE = ("password", "passwd", "token", "authorization",
             "cookie", "secret", "key", "session")


def _mask(value):
    s = str(value)
    if len(s) <= 6:
        return "***"
    return s[:3] + "***" + s[-2:]


def _safe_items(kwargs):
    out = {}
    for k, v in kwargs.items():
        if any(w in k.lower() for w in SENSITIVE):
            out[k] = _mask(v)
        else:
            out[k] = v
    return out

def log_calls(func):
    """记录调用：函数名、脱敏参数、返回值（截断）、耗时、异常"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        safe_kwargs = _safe_items(kwargs)
        print("[call] -> %s args=%s kwargs=%s"
              % (func.__name__, args, safe_kwargs))
        try:
            result = func(*args, **kwargs)
            print("[call] <- %s 返回=%s 耗时=%.3fs"
                  % (func.__name__, _truncate(result), time.perf_counter() - start))
            return result
        except Exception as e:
            print("[call] !! %s 异常=%s: %s 耗时=%.3fs"
                  % (func.__name__, type(e).__name__, e, time.perf_counter() - start))
            raise                      # ← 关键：记完还要抛
    return wrapper


def _truncate(result, limit=80):
    s = str(result)
    return s if len(s) <= limit else s[:limit] + "...(共 %d 字符)" % len(s)

# @log_calls
# def login(username, password):
#     print("登录成功：", username)

# login("zhangsan", password ="P@ssw0rd!")

@log_calls
def get_user(uid, token="abc"):
    if uid == 0:
        raise ValueError("uid 不能为 0")
    return {"id": uid, "name": "张三"}


get_user(1, token="secret-token-123456")
get_user(0)
