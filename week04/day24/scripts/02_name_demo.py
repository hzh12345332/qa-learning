def hello():
    print("hello 被调用了")


print("文件被加载,__name__ =", __name__)

if __name__ == "__main__":
    hello()