import time


class Timer:
    """用 with 计时一个代码块"""

    def __init__(self, name="代码块"):
        self.name = name

    def __enter__(self):
        self.start = time.perf_counter()
        print("[进入] 开始计时：", self.name)
        return self                 # ← 给 as 后面的变量（这里用不上，但要有）

    def __exit__(self, exc_type, exc_val, exc_tb):
        cost = time.perf_counter() - self.start
        print("[退出] %s 耗时 %.3fs" % (self.name, cost))
        return False                # ← False = 不吞异常


with Timer("读文件"):
    time.sleep(0.1)


class Swallow:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("  __exit__ 收到异常：", exc_type.__name__ if exc_type else None)
        return True         # ← True = 吞掉


class NoSwallow:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("  __exit__ 收到异常：", exc_type.__name__ if exc_type else None)
        return False        # ← False = 继续抛

print("=== 返回 True(吞)===")
with Swallow():
    raise ValueError("炸了")
print("  程序还在跑（异常被吞）")

print("=== 返回 False(不吞)===")
try:
    with NoSwallow():
        raise ValueError("炸了")
except ValueError as e:
    print("  外面抓到了：", e)