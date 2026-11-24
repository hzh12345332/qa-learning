import pytest

@pytest.fixture
def base_url():
    return "https://httpbin.org"


def test_base_url(base_url):          # ← 参数名 = fixture 名
    assert base_url.startswith("http")


# def base_url():
#     return "https://httpbin.org"


# def test_base_url(): 
#     f = base_url()
#     assert f.startswith("http")
