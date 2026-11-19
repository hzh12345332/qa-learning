import time
from functools import wraps


def timer(func):
    """打印函数耗时，并原样返回结果"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            return func(*args, **kwargs)
        finally:
            print("[timer] %s %.3fs" % (func.__name__, time.time() - start))
    return wrapper


def log_calls(func):
    """打印每次调用的函数名和参数"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("[call] %s args=%s kwargs=%s" % (func.__name__, args, kwargs))
        return func(*args, **kwargs)
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