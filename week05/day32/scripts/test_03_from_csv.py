import csv

import pytest

DATA = "week04/day23/data/users.csv"


def load_cases():
    """从 CSV 读 → [(userId, expected), ...]"""
    with open(DATA, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
        assert rows, "users.csv 里没有数据（路径错了？文件空了？）"
    return [(r["userId"], int(r["expected"])) for r in rows]


CASES = load_cases()


@pytest.mark.parametrize("userId,expected", CASES, ids=[c[0] for c in CASES],)
def test_user_get(client, cfg, userId, expected):
    r = client.get(cfg["baseUrl"] + cfg["endpoint"],
                   params={"userId": userId},
                   timeout=cfg["timeout"])
    assert r.status_code == expected, "userId=%s 返回 %s" % (userId, r.status_code)
