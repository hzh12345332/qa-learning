import pytest

@pytest.mark.smoke
def test_cfg_follows_env(cfg, env):
    expected = {"test": 10, "prod": 30}
    assert cfg["timeout"] == expected[env], \
        "env=%s 时 timeout 应该是 %s,实际 %s" % (env, expected[env], cfg["timeout"])