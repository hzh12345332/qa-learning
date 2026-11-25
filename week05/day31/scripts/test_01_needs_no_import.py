# week05/day31/scripts/test_01_needs_no_import.py
import json

CONFIG_PATH = "week04/day23/data/config.json"

def test_user_1_ok(client, cfg):
    r = client.get(cfg["baseUrl"] + cfg["endpoint"],
                   params={"userId": "1"}, timeout=cfg["timeout"])
    assert r.status_code == 200

def test_cfg_matches_file(cfg):
    """cfg 必须和磁盘上的 config.json 完全一致 —— 这才叫"真的在读文件" """
    with open(CONFIG_PATH, encoding="utf-8") as f:
        on_disk = json.load(f)
    assert cfg == on_disk