class User:
    """一个用户"""

    def __init__(self, name, age):
        self.name = name      # 实例属性
        self.age = age

    def intro(self):          # 方法
        return "我叫%s，今年%d岁" % (self.name, self.age)


u = User("张三", 18)
print(u.intro())              # 我叫张三，今年18岁
print(u.name)                 # 张三