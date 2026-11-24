import pytest

@pytest.fixture(autouse=True)#autouse=True
def auto_log():
    print("  [auto] 每个用例都自动跑我")
    yield
    print("  [auto] 收尾")


# def test_x():          # ← 参数里没有 auto_log
#     print("  [auto] 用例中")
#     assert True

@pytest.fixture
def base_url():
    return "https://httpbin.org"

@pytest.fixture
def api(base_url):                      # ← 参数也是 fixture
    print("  [setup] api 依赖 base_url =", base_url)
    yield {"url": base_url, "timeout": 10}
    print("  [teardown] api")


def test_chain(api):                    # ← 只要 api，base_url 自动跟上
    assert api["timeout"] == 10