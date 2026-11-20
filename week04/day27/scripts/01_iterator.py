class CountDown:
    """自己实现的迭代器:3 2 1"""

    def __init__(self, start):    # 定义迭代器的初始化方法
        self.n = start            # 定义迭代器的状态

    def __iter__(self):            # 定义迭代器的迭代方法
        return self                 # 迭代器返回自己

    def __next__(self):           # 定义迭代器的下一个元素方法
        if self.n <= 0:
            raise StopIteration     # ← 用异常表示"没了"
        self.n -= 1    # 等价于 self.n = self.n - 1
        return self.n + 1

for x in CountDown(3):
    print(x)
