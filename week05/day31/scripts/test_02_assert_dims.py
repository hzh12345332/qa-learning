def test_assert_five_dims(client, cfg):
    r = client.get(cfg["baseUrl"] + "/get", params={"userId": "1"}, timeout=cfg["timeout"])
    body = r.json()

    assert r.status_code == 200, r.text[:200]
    assert isinstance(body, dict), body
    assert "args" in body, body
    assert body["args"]["userId"] == "1", body
    assert r.elapsed.total_seconds() < 3, r.elapsed 