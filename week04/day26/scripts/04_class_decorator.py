import time
from functools import update_wrapper


class Timer:
    """把函数变成"调用时计时"的对象"""

    def __init__(self, func):
        self.func = func
        self.calls = 0
        self.total = 0.0
        update_wrapper(self, func)      # ← 相当于类的 @wraps

    def __call__(self, *args, **kwargs):
        start = time.perf_counter()
        try:
            return self.func(*args, **kwargs)
        finally:
            cost = time.perf_counter() - start
            self.calls += 1
            self.total += cost
            print("[Timer] %s %.3fs(累计 %d 次 / 共 %.3fs)"
                  % (self.func.__name__, cost, self.calls, self.total))

@Timer
def do_work(n):
    time.sleep(n)


do_work(0.1)
do_work(0.2)
print("统计：", do_work.calls, round(do_work.total, 3))
print("调用次数：", do_work.calls)