from asserts import check_status


def test_fail_with_snapshot(client, cfg):
    r = client.get(cfg["baseUrl"] + cfg["endpoint"], params={"userId": 7})
    check_status(r, 599)