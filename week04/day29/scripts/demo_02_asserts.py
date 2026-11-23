def test_equal():
    actual = 404
    expected = 200
    assert actual == expected          # ① 相等

def test_member():
    body = {"code": -1, "msg": "bad"}
    assert "data" in body              # ② 含于

def test_is_none():
    error = "timeout"
    assert error is None               # ③ 是 None

def test_type():
    body = [1, 2, 3]
    assert isinstance(body, dict)      # ④ 对象的类型