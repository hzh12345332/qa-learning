import time

def run_case():
    """一个测试函数"""
    time.sleep(0.1)
    return "PASS"

# ① 赋值
alias = run_case
print("① alias is run_case →", alias is run_case)
print("   alias()          →", alias())

# ② 当参数
def run_all(cases, on_result):
    for c in cases:
        on_result(c.__name__, c())


run_all([run_case, run_case],
        lambda n, r: print("②", n, "→", r))

# ③ 当返回值
def make_runner(case):
    def wrapper():
        print("   开始：", case.__name__)
        return case()
    return wrapper


wrapped = make_runner(run_case)
print("③ wrapped()        →", wrapped())

# ④ 放容器
REGISTRY = {"ok": run_case}
print("④ REGISTRY['ok']() →", REGISTRY["ok"]())

# ⑤ 函数属性
print("⑤ __name__         →", run_case.__name__)
print("   __doc__          →", run_case.__doc__)