import time


def timer(func):    #定义函数timer，参数为func
    
    def wrapper():    #定义函数wrapper
        start = time.time()    # 记录开始时间
        result = func()                  # 真正干活
        cost = time.time() - start  # 计算耗时
        print("[timer] %s %.3fs" % (func.__name__, cost))    #输出run_case函数的名字和耗时，耗时取三位小数
        return result                    # ← 把结果原样还回去
    return wrapper      # 返回wrapper函数对象。外层返回内层函数，闭包


def run_case():    #模拟一个测试用例
    time.sleep(0.1)    #模拟耗时
    return "PASS"    #返回测试结果


# run_case = timer(run_case)
# for _ in range(5):
#     run_case()    # 循环执行5次，查看start位置对耗时的影响

# 手工套壳
run_case = timer(run_case)    #把run_case函数传给timer函数，返回wrapper函数对象，再把wrapper函数对象赋值给run_case变量。此时run_case变量指向wrapper函数对象
print(run_case())    #输出run_case函数的返回值，即wrapper函数的返回值