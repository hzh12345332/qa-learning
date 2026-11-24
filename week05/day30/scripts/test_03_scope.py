import pytest

@pytest.fixture
def shared_config():
    print("  [setup]    shared_config")
    yield {"timeout": 10}
    print("  [teardown] shared_config")

@pytest.fixture(scope="module")
def module_client():
    print("  [setup]    module_client (module)")
    yield {"n": 1}
    print("  [teardown] module_client (module)")

@pytest.fixture(scope="session")
def session_flag():
    print("  [setup]    session_flag (session)")
    yield "S"
    print("  [teardown] session_flag (session)")

def test_a(shared_config):
    print("    >> test_a")
    assert shared_config["timeout"] == 10


def test_b(shared_config):
    print("    >> test_b")
    assert shared_config["timeout"] > 0


def test_c(module_client, session_flag):
    print("    >> test_c")
    assert module_client["n"] == 1


def test_d(module_client, session_flag):
    print("    >> test_d")
    assert session_flag == "S"