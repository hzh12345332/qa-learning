import pytest

@pytest.fixture()
def cfg():
    """配置 → 从 config.json 读，不再硬编码"""
    return {"baseUrl": "https://example.com"}

@pytest.fixture
def only_in_sub():            # ← 新增：全项目只有这个文件里有
    return "SUB_ONLY"