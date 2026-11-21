import time
from contextlib import contextmanager


@contextmanager
def timer(name="代码块"):
    start = time.perf_counter()
    print("[进入] 开始计时：", name)
    try:
        yield name                  # ← yield 之前 = __enter__，之后 = __exit__
    finally:
        print("[退出] %s 耗时 %.3fs" % (name, time.perf_counter() - start))


with timer("读文件"):
    time.sleep(0.1)