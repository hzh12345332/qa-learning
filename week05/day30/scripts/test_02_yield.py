import pytest

@pytest.fixture
def temp_file():
    print("  [setup] 造一个临时文件")
    f = open("week05/day30/data/tmp_demo.txt", "w", encoding="utf-8")
    f.write("hello")
    yield f                                  # ← 这里"停顿"，把 f 交出去
    print("  [teardown] 关掉文件")
    f.close()


def test_can_write(temp_file):
    print("    >> 用例开始")
    temp_file.write(" world")
    assert True

