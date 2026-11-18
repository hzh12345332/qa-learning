def make_counter():
    count = 0

    def inner():
        nonlocal count
        count += 1
        return count

    return inner


def make_plain():
    def inner():
        return 1          # 不引用外层变量

    return inner


# ① 证明闭包真的带走了变量
c = make_counter()
print("① __closure__      →", c.__closure__)
print("   cell_contents    →", c.__closure__[0].cell_contents)
print("   连续调用         →", c(), c(), c())


# ② 不是闭包的样子
p = make_plain()
print("② 非闭包 __closure__→", p.__closure__)


# ③ late binding
fs = []
for i in range(3):
    fs.append(lambda: i)
print("③ 没有绑定         →", [f() for f in fs])

fs2 = [lambda i=i: i for i in range(3)]
print("   绑定后           →", [f() for f in fs2])


# ④ 闭包带参数
def make_logger(prefix):
    def log(msg):
        print("[%s] %s" % (prefix, msg))
    return log


info = make_logger("INFO")
err = make_logger("ERROR")
info("用例开始")
err("断言失败")