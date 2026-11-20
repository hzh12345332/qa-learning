# # 四种写法：
# nums = [1, 2, 3, 4, 5]

# # ① 列表推导式
# squares = [n * n for n in nums]
# print("列表：", squares)              # [1, 4, 9, 16, 25]

# # ② 字典推导式
# sq_map = {n: n * n for n in nums}
# print("字典：", sq_map)               # {1: 1, 2: 4, ...}

# # ③ 集合推导式
# evens = {n for n in nums if n % 2 == 0}
# print("集合：", evens)                # {2, 4}

# # ④ 生成器表达式（**圆括号**）
# gen = (n * n for n in nums)
# print("生成器对象：", gen)             # <generator object ...>
# print("转成列表：", list(gen))         # [1, 4, 9, 16, 25]


# # 带条件
# nums = [1, 2, 3, 4, 5]

# print([n for n in nums if n % 2 == 1])          # [1, 3, 5]
# print([n * 10 if n > 3 else n for n in nums])   # [1, 2, 3, 40, 50]
# print([n * 10 if n > 3 else n for n in nums if n % 2 == 1])   # [1, 3, 50]


# # 嵌套
# pairs = [(a, b) for a in [1, 2] for b in ["x", "y"]]
# print(pairs)     # [(1, 'x'), (1, 'y'), (2, 'x'), (2, 'y')]

# 列表和生成器内存对比
import sys

lst = [n * n for n in range(1000000)]
gen = (n * n for n in range(1000000))

print("列表大小：", sys.getsizeof(lst), "字节")     # 约 800 万字节
print("生成器大小：", sys.getsizeof(gen), "字节")   # 约 200 字节