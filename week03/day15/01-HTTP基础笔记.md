# Day 15 ｜ HTTP 基础

## 一、一次请求的完整结构

### 1.1 请求报文四块（行 / 头 / 空行 / 体）

```
POST /api/login HTTP/1.1              ← ① 请求行：方法 + 路径 + 协议版本
Host: qa.example.com                  ← ② 请求头（多个 key: value）
Content-Type: application/json
Content-Length: 32
Authorization: Bearer abc123
                                      ← ③ 空行（必须有一行空的，用来分隔头和体）
{"username":"admin","pwd":"123"}      ← ④ 请求体（GET 请求通常没有体）
```

| 块 | 作用 | 测试时你会关心什么 |
| --- | --- | --- |
| ① 请求行 | 方法 + 路径 + 版本 | 路径对不对、方法对不对 |
| ② 请求头 | 元信息 | Content-Type（告诉服务器我发的是什么格式）、Authorization（我是谁） |
| ③ 空行 | 分隔符 | 少了它，服务器会把体当成头的一部分 |
| ④ 请求体 | 真正要传的数据 | 参数对不对、格式对不对 |

### 1.2 响应报文四块

```
HTTP/1.1 200 OK                       ← ① 状态行：版本 + 状态码 + 原因短语
Content-Type: application/json        ← ② 响应头
Content-Length: 33
Set-Cookie: session=xyz; HttpOnly
                                      ← ③ 空行
{"token":"abc123","expires":3600}     ← ④ 响应体（真正你要的数据）
```

| 块 | 作用 | 测试时你会关心什么 |
| --- | --- | --- |
| ① 状态行 | 状态码 ← 断言第一来源 | 200？401？500？ |
| ② 响应头 | 元信息 | Content-Type（返回的是什么格式）、Set-Cookie（有没有种会话） |
| ③ 空行 | 分隔符 | — |
| ④ 响应体 | 业务数据 | 字段有没有、值对不对、类型对不对 |

- 状态码先看，响应体再看。

### 1.3 我的 curl -v 输出（贴进来）

**输入**

```bash
curl -v https://www.baidu.com -o /dev/null
```

**输出**

```
* Host www.baidu.com:443 was resolved.
* IPv6: (none)
* IPv4: 183.2.172.177
*   Trying 183.2.172.177:443...
* schannel: disabled automatic use of client certificate
* ALPN: curl offers http/1.1
* ALPN: server accepted http/1.1
* Established connection to www.baidu.com (183.2.172.177 port 443) from 192.168.0.101 port 61796
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed
  0      0   0      0   0      0      0      0                              0* using HTTP/1.x
```

## 二、方法

### 2.1 七个方法 + 安全 / 幂等

| 方法 | 安全（不改数据） | 幂等（重复发结果一样） | 典型用途 |
| --- | --- | --- | --- |
| GET | ✅ | ✅ | 查询 |
| HEAD | ✅ | ✅ | 只要响应头（GET 的无体版） |
| POST | ❌ | ❌ | 创建 / 提交（每次都可能产生新数据） |
| PUT | ❌ | ✅ | 全量替换 |
| PATCH | ❌ | ❌（规范不保证） | 部分更新 |
| DELETE | ❌ | ✅ | 删除 |
| OPTIONS | ✅ | ✅ | 查这个接口支持哪些方法（跨域预检用） |

### 2.2 POST vs PUT、PUT vs PATCH

| 对比 | 区别 |
| --- | --- |
| POST vs PUT | POST 不幂等（发两次可能建两条）；PUT 幂等（发两次结果一样，因为它是"覆盖成这个样子"） |
| PUT vs PATCH | PUT 是全量替换（没传的字段会被清空/置默认）；PATCH 是只改传了的字段 |

## 三、状态码

### 3.1 五大类

| 类 | 含义 | 一句话 |
| --- | --- | --- |
| 1xx | 信息 | 还在处理（日常几乎见不到） |
| 2xx | 成功 | 干成了 |
| 3xx | 重定向 | 你去别处拿 |
| 4xx | 客户端错 | 你（调用方）有问题 |
| 5xx | 服务端错 | 我（服务器）有问题 |

### 3.2 我背下来的 14 个（默写一遍）

| 码 | 名称 | 什么时候出现 | 测试时怎么用 |
| --- | --- | --- | --- |
| 200 | OK | 成功 | 正常用例的断言值 |
| 201 | Created | 创建成功 | POST 新增成功的断言值 |
| 204 | No Content | 成功但没响应体 | DELETE 成功常见 |
| 301 | 永久重定向 | 域名换了 | 检查有没有跳对 |
| 302 | 临时重定向 | 登录后跳首页 | 登录接口常返回这个 |
| 304 | Not Modified | 缓存没变 | 缓存策略 |
| 400 | Bad Request | 参数格式错、缺必填 | 参数校验的断言值 |
| 401 | Unauthorized | 未登录 / token 失效 | 鉴权用例的断言值 |
| 403 | Forbidden | 登录了但没权限 | 越权用例的断言值 |
| 404 | Not Found | 路径不存在 | 路径写错、资源被删 |
| 405 | Method Not Allowed | 方法不对（该 GET 你发 POST） | 方法覆盖测试 |
| 500 | Internal Server Error | 服务端抛异常 | 任何 500 都是 Bug |
| 502 | Bad Gateway | 网关后面的服务挂了 | 部署/重启时常见 |
| 503 | Service Unavailable | 服务过载/维护中 | 压测时会看到 |

### 3.3 401 vs 403、400 vs 500

- 401 vs 403：401 = 你没证明你是谁（该带 token 没带，或 token 过期） 403 = 你证明了你是谁，但你没这个权限（普通用户去调管理员接口）
- 400 vs 500：400是缺字段、类型错、JSON 语法坏属于调用方的问题，500是服务端抛异常属于服务端的问题

## 四、Header

### 4.1 请求头 / 响应头各记 5 个

**请求头**

| Header | 作用 | 测试关注点 |
| --- | --- | --- |
| Host | 我要访问哪个域名 | 多域名部署时 |
| User-Agent | 我是什么客户端 | 有些接口按 UA 返回不同内容 |
| Content-Type | 我发的是什么格式 | 最常出错的一个 |
| Authorization | 我是谁（token） | 鉴权测试 |
| Cookie | 会话凭据 | 会话保持 |
| Accept | 我能接受什么格式 | 内容协商 |

**响应头**

| Header | 作用 | 测试关注点 |
| --- | --- | --- |
| Content-Type | 我返回的是什么格式 | 断言格式对不对 |
| Content-Length | 响应体多长 | 中文/压缩时会变 |
| Set-Cookie | 给你种个会话 | 登录后有没有下发 |
| Location | 重定向去哪 | 配合 3xx 看 |
| Cache-Control | 缓存策略 | 缓存测试 |

- Content-Length 是字节数，不是字符数。中文在 UTF-8 下占 3 字节：张三 是 6 字节，不是 2。

### 4.2 Content-Type 四种格式 + 发错的后果

**同一个接口，body 用不同格式发，服务器解析结果完全不同**

| Content-Type | body 长什么样 | Postman 里选什么 |
| --- | --- | --- |
| application/json | {"name":"张三"} | Body → raw → JSON |
| application/x-www-form-urlencoded | name=张三&age=20 | Body → x-www-form-urlencoded |
| multipart/form-data | 带边界的分段（用于文件上传） | Body → form-data |
| text/plain | 纯文本 | 很少用 |

```
你发 JSON 字符串，但 Content-Type 写成 x-www-form-urlencoded
        ↓
服务器按"表单"去解析 → 解析出 0 个字段
        ↓
报 400（参数缺失）或 500（空指针）
        ↓
你以为是接口坏了，其实是自己发错格式
```

- 90% 的“明明参数传了却报缺参数”，都是 Content-Type 选错。

## 五、五个实验的输出

### 5.1 完整报文（实验 1）

**输入**

```bash
curl -v https://www.baidu.com -o /dev/null
```

**输出**

```
> GET / HTTP/1.1
> Host: www.baidu.com
> User-Agent: curl/8.21.0
> Accept: */*
>
* Request completely sent off
< HTTP/1.1 200 OK
< Cache-Control: private, no-cache, no-store, proxy-revalidate, no-transform
< Content-Length: 2443
< Content-Type: text/html
< Pragma: no-cache
< Server: bfe
< Set-Cookie: BDORZ=27315; max-age=86400; domain=.baidu.com; path=/
< Date: Fri, 06 Nov 2026 06:45:21 GMT
<
{ [512 bytes data]
100   2443 100   2443   0      0  19122      0                              0
* Connection #0 to host www.baidu.com:443 left intact
```

### 5.2 三种状态码（实验 3）

**200：正常**

```bash
code=$(curl -s -o /dev/null -w "%{http_code}" https://www.baidu.com)
echo "期望=200 实际=$code"
```

**输出**

```
期望=200 实际=200
```

**404：路径不存在**

```bash
code=$(curl -s -o /dev/null -w "%{http_code}" https://www.baidu.com/this-page-does-not-exist)
echo "期望=404 实际=$code"
```

**输出**

```
期望=404 实际=404
```

**405：方法不对（对静态文件发 POST）**

```bash
code=$(curl -s -o /dev/null -w "%{http_code}" -X POST https://www.baidu.com)
echo "期望=405 实际=$code"
```

**输出**

```
期望=405 实际=200
```

- 百度首页是静态资源，nginx 根本不校验方法。五个方法全试一遍，连 HELLO（世界上不存在的方法）都回 200 —— 彻底说明：服务器压根没看方法。

**五个方法**

```bash
for m in GET POST DELETE PUT HELLO; do printf "%-7s -> " "$m"; curl -s -o /dev/null -w "%{http_code}\n" -X "$m" https://www.baidu.com; done
```

**结果**

```
GET     -> 200
POST    -> 200
DELETE  -> 200
PUT     -> 200
HELLO   -> 200
```

### 5.3 两种 Content-Type（实验 4）

#### 百度首页（HTML）

**输入**

```bash
curl -sI https://www.baidu.com | grep -i "^content-type:"
```

**输出**

```
Content-Type: text/html
```

#### github首页（JSON）

**输入**

```bash
curl -sI https://api.github.com | grep -i "^content-type:"
```

**输出**

```
Content-Type: application/json; charset=utf-8
```

### 5.4 重定向（实验 5）

#### 看跳转目标 → 用 redirect_url（不加 -L）

- 预期：看到 301/302，停在第一站

**输入**

```bash
curl -s -o /dev/null -w "%{http_code} -> %{redirect_url}\n" http://github.com
```

**输出**

```
301 -> https://github.com/
```

#### 看最终落地 → 用 url_effective（加 -L）

- 预期：跟着跳到底

**输入**

```bash
curl -sL -o /dev/null -w "%{http_code} -> %{url_effective}\n" http://github.com
```

**输出**

```
200 -> https://github.com/
```

## 六、用 HTTP 设计用例

### 6.1 状态码 → 用例类型对照表

| 你想测什么 | 怎么造 | 期望状态码 |
| --- | --- | --- |
| 正常流程 | 合法参数 | 200 / 201 |
| 参数校验 | 缺必填、类型错、超长、空值 | 400 |
| 鉴权 | 不带 token / token 过期 / 伪造 token | 401 |
| 越权 | 用 A 用户的 token 查 B 用户的数据 | 403 |
| 资源不存在 | 用一个不存在的 id | 404 |
| 方法覆盖 | 对 GET 接口发 POST | 405 |
| 格式校验 | 发 XML 给一个只收 JSON 的接口 | 415 |
| 重复提交 | 同一个 POST 连发两次 | 看业务（可能 200 建两条，也可能 409） |

### 6.2 幂等性与重复提交

| 接口 | 重复发两次会怎样 | 该测什么 |
| --- | --- | --- |
| POST /order | 可能建两条订单 | 重复提交是 Bug 吗？ 看业务（下单要防重） |
| PUT /user/1 | 结果和发一次一样 | 幂等，重复调用安全 |
| DELETE /user/1 | 第一次 204，第二次可能 404 | 要测“重复删除”的表现 |

### 6.3 我写的一个登录接口用例草稿

#### 接口：POST /api/login

| # | 用例 | 请求 | 期望状态码 | 期望响应 |
| --- | --- | --- | --- | --- |
| 1 | 正常登录 | {"user":"admin","pwd":"正确"} | 200 | data.token 存在且非空、且能访问下一个接口 |
| 2 | 密码错误 | {"user":"admin","pwd":"错"} | 401 | 无 data.token；msg 为通用文案 |
| 3 | 缺密码字段 | {"user":"admin"} | 400 | 提示缺参数 |
| 4 | 用户名不存在 | {"user":"nobody","pwd":"x"} | 401 | 状态码、msg、响应体结构与 #2 逐字一致 |
| 5 | 空 body | （空） | 400 | 不能 500 |
| 6 | Content-Type 错 | 用 form 发 JSON 字符串 | 400 / 415 | 明确的格式错误 |
| 7 | 超长用户名 | 1000 个字符 | 400 | 不能 500、不能崩 |

## 七、自检 10 题（2026-11-06）

| # | 题 | 一句话答案 |
| --- | --- | --- |
| 1 | 请求报文四块是什么，空行有什么用 | 四块分别是请求行、请求头、空行、请求体。空行的作用是分隔请求头和请求体 |
| 2 | > 和 < 在 curl -v 输出里分别代表什么 | >代表是我发送的，<代表是我接收的 |
| 3 | GET / POST / PUT / PATCH / DELETE 各自幂等吗 | GET,DELETE,PUT是幂等的；POST,PATCH不是幂等的 |
| 4 | PUT 和 PATCH 的本质区别 | PUT是覆盖，就是全部换新。PATCH是修改部分换新 |
| 5 | 401 和 403 的区别 | 401是没有登录，403是登录了没有权限 |
| 6 | 4xx 和 5xx 的责任方分别是谁 | 4xx责任方是调用端，5xx责任方是服务端 |
| 7 | 405 什么时候出现，它对应哪类测试 | 方法不对的时候出现，方法覆盖测试 |
| 8 | 四种 Content-Type + 发错会怎样 | 提交了参数却还是显示缺少参数。四种 Content-Type：`application/json`,`application/x-www-form-urlencoded`,`multipart/form-data`,`text/plain` |
| 9 | 为什么 HTTP 要"无状态"、靠什么维持会话 | - |
| 10 | 一个登录接口，你能列出几类用例 | - |

## 八、还没搞懂的 → 已弄明白

### 1. 为什么 HTTP 要"无状态"、靠什么维持会话

- HTTP 无状态是为了可扩展：任何服务器都能处理任何请求，不用共享内存，加机器就能扩容。代价是服务器不记得你，所以要把身份每次带上 —— 传统做法是 Cookie + Session（服务端存状态），现代做法是 Token/JWT（客户端存、服务端验签，真正无状态）。

**测试视角**

| 方案 | 必测的点 | 为什么 |
| --- | --- | --- |
| Cookie/Session | 不发 Cookie 时是否 401、Cookie 过期、集群下换机器是否还能认 | session 没共享是经典 Bug |
| Token/JWT | token 过期、篡改 payload 后是否被拒、注销后 token 是否立即失效 | JWT 天然做不到“立即失效”，这是著名缺陷 |

- 高频BUG：JWT 是“自证”的，服务端不存，所以用户点“退出登录”后，那个 token 在过期前依然有效。要真正踢下线，必须加黑名单（等于又变成有状态了）。

### 2. 405 什么时候出现，它对应哪类测试

- 出现条件（缺一不可）：路径匹配上了某个接口/资源。该接口没有实现你用的方法。

**对应哪类测试**

- 方法覆盖测试，属于“接口契约测试”的一部分。用例这样写：

| # | 用例 | 期望 |
| --- | --- | --- |
| 1 | 只支持 GET 的接口 → 发 POST | 405 + Allow 含 GET |
| 2 | 同上 → 发 DELETE | 405 |
| 3 | 发一个不存在的方法（HELLO） | 400 或 501（看框架），绝不能 500 |
| 4 | 发支持的方法（GET） | 200（基线，证明前面的 405 不是因为接口坏了） |

### 3. 一个登录接口，你能列出几类用例

- 我按参数、凭据、异常、安全、会话五个维度拆：参数测缺空类型超长；凭据测密码错和用户不存在，两者响应必须一致防枚举；异常测空 body、错 Content-Type、注入串，要求都不 500；安全测爆破锁定和信息泄露；会话测 token 过期和注销失效。
