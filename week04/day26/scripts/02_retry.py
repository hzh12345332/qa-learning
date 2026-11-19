import time
from functools import wraps


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
                    print("[retry] 第 %d 次失败：%s,%.1fs 后重试"
                          % (i + 1, type(e).__name__, delay))
                    if delay:
                        time.sleep(delay)
            # 这行其实到不了，for 里要么 return 要么 raise
        return wrapper
    return deco

@retry(times=3, delay=0.1, exceptions=(ValueError,))
def flaky():
    """前两次失败，第三次成功"""
    if not hasattr(flaky, "_n"):
        flaky._n = 0
    flaky._n += 1
    print("  第 %d 次尝试" % flaky._n)
    if flaky._n < 3:
        raise ValueError("模拟偶发失败")
    return "OK"
print("成功场景：", flaky())

@retry(times=2, delay=0, exceptions=(ValueError,))
def always_fail():
    raise ValueError("永远失败")

try:
    always_fail()
except ValueError as e:
    print("最后一次失败被抛出：", e)