import pytest
import requests


# ---------- fixture 区：这一块以后会挪到 conftest.py ----------
@pytest.fixture(scope="function")   # 每条用例创建一次
# @pytest.fixture(scope="session")  # 全局创建一次
def cfg():
    """只读配置 → session 作用域，整轮建一次"""
    return {"baseUrl": "https://httpbin.org", "timeout": 10, "endpoint": "/get"}

@pytest.fixture(scope="function")   # 每条用例创建一次
# @pytest.fixture(scope="session")  # 全局创建一次
def client(cfg):
    """有状态、要关 → 但整轮只建一次（跑完才关）"""
    s = requests.Session()
    print("  [setup] Session 建好了")
    yield s
    s.close()
    print("  [teardown] Session 关掉了")


# ---------- 用例区：只有"发请求 + 断言" ----------

def test_user_1_ok(client, cfg):
    r = client.get(cfg["baseUrl"] + cfg["endpoint"],
                   params={"userId": "1"}, timeout=cfg["timeout"])
    assert r.status_code == 200


def test_user_2_ok(client, cfg):
    r = client.get(cfg["baseUrl"] + cfg["endpoint"],
                   params={"userId": "2"}, timeout=cfg["timeout"])
    assert r.status_code == 200


def test_status_404(client, cfg):
    r = client.get(cfg["baseUrl"] + "/status/404", timeout=cfg["timeout"])
    assert r.status_code == 404