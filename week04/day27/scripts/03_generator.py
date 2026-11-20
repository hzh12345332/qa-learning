# # 递减
# def count_down(n):
#     while n > 0:
#         yield n
#         n -= 1


# for x in count_down(3):
#     print(x)



# # 看demo调用的时候干了什么，以及yield的作用
# def demo():
#     print("① 开始")
#     yield 1
#     print("② 继续")
#     yield 2
#     print("③ 结束")


# print("--- 调用 demo() ---")
# g = demo()
# print("--- 拿到：", g)

# print("--- 第一次 next ---")
# print(next(g))

# print("--- 第二次 next ---")
# print(next(g))

# print("--- 第三次 next ---")
# try:
#     next(g)
# except StopIteration:
#     print("--- StopIteration:结束了 ---")


# # 确认局部变量在暂停的时候被保存了
# def counter():
#     n = 0
#     while True:
#         n += 1
#         yield n

# c = counter()
# print("取第一次：", next(c))
# print("取第二次：", next(c))
# print("取第三次：", next(c))


# # send() 方法可以向生成器发送一个值，这个值会被 yield 表达式接收
# def echo():
#     while True:
#         got = yield                 # yield 把 send 进来的值接住
#         print("收到：", got)


# g = echo()
# next(g)                             # 必须先"启动"一次，跑到第一个 yield
# g.send("hello")                     # 收到： hello
# g.send("world")                     # 收到： world



# # 确认生成器也是一次性的
# def gen():
#     yield 1
#     yield 2


# g = gen()
# print(list(g))      # [1, 2]
# print(list(g))      # []


# 提前退出：break 走了，生成器怎么办
def read_lines():
    print("  打开资源")
    try:
        yield "第一行"
        yield "第二行"
    finally:
        print("  释放资源")        # ← 一定会执行

g = read_lines()
print(next(g))          # 打开资源 / 第一行
print(next(g))          # 第二行
print("--- 不玩了 ---")
g.close()               # 释放资源        ← 显式关闭，finally 会跑


# def gen():
#     try:
#         print("开始")
#         yield 1
#     finally:
#         print("结束")
# g = gen()
# print(next(g))          # 开始 / 1