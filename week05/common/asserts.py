def check_status(r, expected):
    """第 1 层：传输层。状态码不对，后面全不用看。"""
    assert r.status_code == expected, \
        "[传输层] 状态码：期望 %s，实际 %s" % (expected, r.status_code)
    return r


def check_json(r):
    """第 2 层：结构层。是不是 JSON,能不能解析。"""
    try:
        return r.json()
    except ValueError:
        raise AssertionError("[结构层] 响应不是 JSON，前 200 字：%r" % r.text[:200])


def check_fields(data, required):
    """第 2 层续：该有的字段在不在。"""
    missing = [k for k in required if k not in data]
    assert not missing, \
        "[结构层] 缺字段 %s（实际有：%s）" % (missing, sorted(data))


def check_no_extra_fields(data, allowed):
    """多余字段：实际有、但不在允许清单里"""
    extra = [k for k in data if k not in allowed]
    assert not extra, "[结构层] 多出字段 %s（允许：%s）" % (extra, sorted(allowed))


def check_value(data, key, expected):
    """第 3 层：业务层。值对不对。"""
    actual = data.get(key)
    assert actual == expected, \
        "[业务层] %s：期望 %r，实际 %r" % (key, expected, actual)