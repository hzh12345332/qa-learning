import time
from functools import wraps


# ① 手工版
def timer_manual(func):
    def wrapper():
        start = time.time()
        result = func()
        print("① [手工] %s %.3fs" % (func.__name__, time.time() - start))
        return result
    return wrapper


def job():
    time.sleep(0.1)
    return "PASS"


job = timer_manual(job)
print("   返回 →", job())


# ② 不加 wraps
def timer_raw(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            return func(*args, **kwargs)
        finally:
            print("② [无wraps] %.3fs" % (time.time() - start))
    return wrapper


@timer_raw
def job2(x, y=1):
    """业务说明"""
    return x + y


print("   返回 →", job2(1, y=2))
print("   __name__ →", job2.__name__)      # wrapper
print("   __doc__  →", job2.__doc__)       # None


# ③ 加 wraps
def timer_wrapped(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            return func(*args, **kwargs)
        finally:
            print("③ [有wraps] %s %.3fs" % (func.__name__, time.time() - start))
    return wrapper


@timer_wrapped
def job3(x, y=1):
    """业务说明"""
    return x + y


print("   返回 →", job3(1, y=2))
print("   __name__ →", job3.__name__)      # job3
print("   __doc__  →", job3.__doc__)       # 业务说明


# ④ 异常也要能被看见（finally 不吞异常）
@timer_wrapped
def job4():
    raise ValueError("故意失败")


try:
    job4()
except ValueError as e:
    print("④ 异常没有被吞掉 →", e)