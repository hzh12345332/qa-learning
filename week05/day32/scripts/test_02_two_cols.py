import pytest

CASES = [("1", 200), ("2", 200), ("999", 200)]


@pytest.mark.parametrize("userId,expected", CASES)
def test_user_get(client, cfg, userId, expected):
    r = client.get(cfg["baseUrl"] + cfg["endpoint"],
                   params={"userId": userId},
                   timeout=cfg["timeout"])
    assert r.status_code == expected, "userId=%s 返回 %s" % (userId, r.status_code)