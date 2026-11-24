# week05/day30/scripts/demo_06_error.py
# ⚠️ 这个文件故意全是 ERROR —— 用 demo_ 开头，不进全量收集
import pytest


# ---------- 错误一：参数名找不到对应 fixture ----------
def test_need_missing(no_such_fixture):
    assert True


# ---------- 错误二：fixture 内部抛异常 ----------
@pytest.fixture
def broken():
    raise RuntimeError("配置读不到")
    yield None


def test_use_broken(broken):
    assert True