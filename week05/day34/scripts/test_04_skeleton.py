import pytest
from asserts import check_status, check_json, check_fields, check_value


@pytest.mark.smoke
def test_user_get(client, cfg, row):
    r = client.get(cfg["baseUrl"] + cfg["endpoint"],
                   params={"userId": row["userId"]},
                   timeout=cfg["timeout"])
    check_status(r, 200)
    data = check_json(r)
    check_fields(data, ["args", "headers", "url"])
    check_value(data["args"], "userId", row["userId"])