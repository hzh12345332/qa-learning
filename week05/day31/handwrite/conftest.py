import pytest
import requests
import json

CONFIG_PATH = "week04/day23/data/config.json"


def load_config(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture(scope="function")
def cfg():
    return load_config(CONFIG_PATH)

@pytest.fixture(scope="session")
def client():
    s = requests.Session()
    yield s
    s.close()