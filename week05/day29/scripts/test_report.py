import requests

BASE_URL = "https://httpbin.org"
TIMEOUT = 10


def get(uid):
    """把"发请求"收在一处，以后换成 ApiClient 只改这里"""
    return requests.get(BASE_URL + "/get", params={"userId": uid}, timeout=TIMEOUT)


def test_user_1_ok():
    r = get("1")
    assert r.status_code == 200


def test_user_2_ok():
    r = get("2")
    assert r.status_code == 200


def test_status_404_returns_404():
    # 这条不用 userId：httpbin 的 /status/404 一定会返回 404
    r = requests.get(BASE_URL + "/status/404", timeout=TIMEOUT)
    assert r.status_code == 404

def test_user_999_ok():
    r = get("999")
    assert r.status_code == 200, "userId=999 返回 %s,响应体是 %s" % (r.status_code, r.text[:200])