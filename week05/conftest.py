import json
import os
import csv


import pytest
import requests



# 数据还在 day23（别复制，直接读）
CONFIG_PATH = "week04/day23/data/config.json"
DATA_PATH = "week04/day23/data/users.csv"


def load_config(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def cfg():
    """配置 → 从 config.json 读，不再硬编码"""
    return load_config(CONFIG_PATH)


@pytest.fixture(scope="session")
def client(cfg):
    s = requests.Session()
    yield s
    s.close()

@pytest.fixture
def only_in_sub():
    return "SUB_ONLY"


def load_cases(path):
    """读 CSV → 每行一个 dict(不是元组！)"""
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows, "users.csv 里没有数据（路径错了？文件空了？）"
    return rows


# ---- 数据层：测试函数里出现 "row" 这个名字，就自动展开 ----
def pytest_generate_tests(metafunc):
    if "row" in metafunc.fixturenames:
        rows = load_cases(DATA_PATH)
        metafunc.parametrize("row", rows, ids=[r["userId"] for r in rows])
