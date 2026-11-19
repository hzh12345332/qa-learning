from functools import wraps


def retry(times):
    print("① retry 被调用,times =", times)

    def deco(func):
        print("② deco 被调用，收到", func.__name__)

        @wraps(func)
        def wrapper(*args, **kwargs):
            print("③ wrapper 被调用,args =", args)
            return func(*args, **kwargs)

        return wrapper
    return deco


@retry(times=3)
def do_work(x):
    return x * 2
#do_work = retry(times=3)(do_work)

print("--- 定义完了 ---")
print("结果：", do_work(5))