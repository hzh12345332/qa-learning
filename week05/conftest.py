import json
import os

import pytest
import requests

# 数据还在 day23（别复制，直接读）
CONFIG_PATH = "week04/day23/data/config.json"


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