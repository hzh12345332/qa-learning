def test_user_get(client, cfg, row):
    r = client.get(cfg["baseUrl"] + cfg["endpoint"],
                   params={"userId": row["userId"]},
                   timeout=cfg["timeout"])
    assert r.status_code == int(row["expected"]), "userId=%s 返回 %s" % (
        row["userId"], r.status_code)
