import pytest

@pytest.mark.parametrize("uid", ["1", "2", "999"])
def test_uid(uid):
    assert uid.isdigit()

@pytest.mark.parametrize(
    "a,b",
    [
        (1, 200),
        pytest.param(2, 404, marks=pytest.mark.xfail(reason="故意失败：演示失败报告")),
    ],
)
def test_no_ids(a, b):
    assert b == 200