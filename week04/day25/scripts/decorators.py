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