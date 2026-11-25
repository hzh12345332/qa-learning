# week05/day31/scripts/test_sibling_sub.py
# 【演示】fixture 可见范围：只往下、不往上传
# only_in_sub 定义在 sub/conftest.py 里；这条测试在父目录 scripts/ 下。
#   - 删掉 scripts/conftest.py 后跑 → fixture 'only_in_sub' not found
#   - 保留 scripts/conftest.py  后跑 → PASSED
import pytest  # noqa: F401

def test_use_sub_fixture(only_in_sub):
    assert only_in_sub == "SUB_ONLY"