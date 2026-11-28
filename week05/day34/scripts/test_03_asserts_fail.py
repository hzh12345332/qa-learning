import pytest
from asserts import check_status, check_json, check_fields, check_value, check_no_extra_fields


def test_three_layers_pass(client, cfg):
    r = client.get(cfg["baseUrl"] + cfg["endpoint"], params={"userId": 1})
    check_status(r, 200)
    data = check_json(r)
    check_fields(data, ["args", "headers", "url"])
    check_value(data["args"], "userId", "1")

@pytest.mark.xfail
def test_layer2_missing_field(client, cfg):
    r = client.get(cfg["baseUrl"] + cfg["endpoint"], params={"userId": 2})
    check_status(r, 200)
    data = check_json(r)
    check_fields(data, ["args", "headers", "data", "data1", "data2"])      # ← 故意


@pytest.mark.xfail
def test_layer2_extra_field(client, cfg):
    r = client.get(cfg["baseUrl"] + cfg["endpoint"], params={"userId": 4})
    check_status(r, 200)
    data = check_json(r)
    # 只允许 args，实际有 5 个字段 → 应该报"多出 4 个"
    check_no_extra_fields(data, ["args"])


@pytest.mark.xfail
def test_layer3_wrong_value(client, cfg):
    r = client.get(cfg["baseUrl"] + cfg["endpoint"], params={"userId": 3})
    check_status(r, 200)
    data = check_json(r)
    check_fields(data, ["args"])
    check_value(data["args"], "userId", "999")                   # ← 故意