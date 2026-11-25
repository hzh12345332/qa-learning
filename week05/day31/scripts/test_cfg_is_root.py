def test_cfg_is_root(cfg):
    print("  scripts/ 拿到的 cfg =", cfg)
    assert cfg["baseUrl"] == "https://httpbin.org"