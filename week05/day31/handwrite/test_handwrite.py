def test_user_1(client, cfg):
    r = client.get(cfg["baseUrl"] + cfg["endpoint"],
                   params={"userId": "1"},
                   timeout=cfg["timeout"])
    assert r.status_code == 200

def test_user_2(client, cfg):
    r = client.get(cfg["baseUrl"] + cfg["endpoint"],
                   params={"userId": "2"},
                   timeout=cfg["timeout"])
    assert r.status_code == 200

def test_status_404(client, cfg):
    r = client.get(cfg["baseUrl"] + "/status/404",
        timeout=cfg["timeout"])
    assert r.status_code == 404