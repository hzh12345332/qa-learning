# HTTPBin-接口测试集合（M1 产出）

> 一套能一键批量执行的接口测试集合：11 条请求 / 29 条断言 / 覆盖鉴权、变量传递、异常状态。

## 一、怎么跑（30 秒）

1. Postman → `Import` → 选 `HTTPBin-接口测试集合.postman_collection.json`
2. **不用配环境**（`baseUrl` 已内置在集合变量里，默认 `https://httpbin.org`）
3. 集合右键 → `Run` → `Run HTTPBin 接口测试集合`
4. 看顶部汇总：`All tests` / `Passed` / `Failed`

> 换环境时：新建环境，加一个 `baseUrl` 覆盖即可（环境变量优先级高于集合变量）。

## 二、覆盖了什么

| 场景 | 请求 | 验证点 |
|---|---|---|
| 鉴权 - 无凭证 | 01 | 401，且失败响应不含 token |
| 鉴权 - 带凭证 | 02 | 200，`authenticated: true` |
| 请求体回显 | 03 | 我发的 name / tags 原样返回 |
| Cookie 缺省 | 04 | 无 cookie → 空对象 |
| Cookie 传递 | 04b | 带 `session=abc123` → 回显一致 |
| 变量传递 | 05 → 06 | uuid 从 05 传到 06 |
| 动态变量 | 07 | uuid 格式 / timestamp 正整数 / randomInt 范围 |
| 异常状态码 | 08 / 09 | 500 / 404，且 body 为空（不泄露） |
| 延迟 | 10 | `/delay/3` 最终返回 200 |

## 三、断言分层

- **L1 协议**：状态码、Content-Type
- **L2 数据**：字段值、数组长度、回显一致
- **L3 业务/安全**：401 不含 token、5xx body 为空

## 四、已知限制

- **httpbin 不校验业务规则**：`/bearer` 只验格式不验值，`/get` 不校验 `userId` 是否存在 —— 所以这套用例测的是"协议和链路"，不是"业务正确性"
- **不写响应时间断言**：公网接口会随机失败
- **06 依赖 05 的执行顺序**：Runner 按集合顺序跑，别拖动顺序

## 五、演示失败信息

把 `09-模拟 404` 的断言临时改成期望 200，跑一次 →
`Failed 1`，报告里能看到：请求名 / 断言名 / `expected 200 but got 404`。
（演示完已改回）

## 六、维护规则（**改完集合必须照做**）

### 6.1 导出后必查集合变量 —— Postman 会把它清空

**已验证两次（2026-11-19、2026-11-21）：Postman 每次导出都会把集合变量的 `initial` 值清掉。**

不检查的后果：`baseUrl` 变空 → 别人导入后所有请求都失败，"一键导入即跑"直接失效。

**导完立刻跑这段检查**：

```bash
"C:/Users/86177/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/python.exe" -c "
import json,io,sys
sys.stdout.reconfigure(encoding='utf-8')
d=json.load(io.open('week03/postman/HTTPBin-接口测试集合.postman_collection.json',encoding='utf-8'))
print([(v['key'], v['value']) for v in d['variable']])"
```

**正确输出**（`uid` 本来就应该空）：

```
[('uid', ''), ('baseUrl', 'https://httpbin.org'), ('token', 'test-token-123')]
```

**看到 `baseUrl` 或 `token` 是空字符串 → 手动填回去再提交。**

### 6.2 别用 `grep -c` 数断言

Postman 把整个脚本压成 JSON 里的**一个字符串**，所以 `grep -c "pm.test("` 数的是"有多少行命中"，
不是断言条数（一个请求只占 1 行）。**正确数法**：

```bash
"C:/Users/86177/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/python.exe" -c "
import json,io,sys
sys.stdout.reconfigure(encoding='utf-8')
d=json.load(io.open('week03/postman/HTTPBin-接口测试集合.postman_collection.json',encoding='utf-8'))
tot=0
for it in d['item']:
    n=sum('\n'.join(e.get('script',{}).get('exec',[])).count('pm.test(') for e in it.get('event',[]) if e.get('listen')=='test')
    tot+=n; print('%-26s %d' % (it['name'], n))
print('TOTAL', tot)"
```

**断言数变了，记得同步改第 3 行的汇总数字。**

### 6.3 导出前后的固定流程

1. Postman 里改完断言 → 右键集合 → `Export` → **Collection v2.1**（整个集合，不是单个请求）
2. 覆盖 `week03/postman/HTTPBin-接口测试集合.postman_collection.json`
3. 跑 6.1 的变量检查（**必做**）
4. 跑 6.2 的断言统计，同步 README 第 3 行的数字
5. `git diff week03/postman/` —— **确认只改了该改的请求**
6. 单独一条 commit：`test: xx 请求补 xxx 断言（N 条）`

> **别靠记忆，靠文件。** 这条规则就是被两次同样的坑逼出来的。

