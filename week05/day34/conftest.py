import json

import pytest
import requests

def pytest_addoption(parser):
    """注册自定义命令行参数"""
    parser.addoption("--env", default="test", choices=["test", "prod"],
                     help="选哪份配置:test / prod")


@pytest.fixture(scope="session")
def env(request):
    """把命令行参数变成 fixture"""
    return request.config.getoption("--env")

@pytest.fixture(scope="session")
def cfg(env):
    path = "week05/day34/config/%s.json" % env
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    print("\n[cfg] 加载了 %s → %s" % (path, data))    # 整个进程只打一次
    return data

@pytest.fixture
def trace(request):
    """每条用例一份请求记录，挂在 test item 上"""
    request.node._trace = []
    return request.node._trace


@pytest.fixture
def client(cfg, trace):
    """function 级：每条用例一个 Session,每个响应自动记进 trace"""
    s = requests.Session()

    def record(resp, *args, **kwargs):
        trace.append("%s %s -> %s" % (resp.request.method, resp.url, resp.status_code))

    s.hooks["response"].append(record)
    yield s
    s.close()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.failed:
        trace = getattr(item, "_trace", None)
        if trace is not None:
            rep.sections.append(("请求快照", "\n".join(trace) or "（这次没发出请求）"))