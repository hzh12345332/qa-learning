# Day 17 ｜ Postman 基础

## 一、Postman 与 curl 的对应关系

### 1.1 五个区块 → 报文四块（表格）

| Postman 标签 | 对应报文哪一块 | 新手最常犯的错 |
| --- | --- | --- |
| 方法 + URL | 请求行 | 方法选错（该 GET 选 POST） |
| Params | URL 的 query | 以为它是"独立的参数" |
| Headers | 请求头 | 忘了 Content-Type |
| Body | 请求体 | 选了 raw 但没选 JSON |
| Authorization | 请求头的一种（自动生成） | 手写了头，又在 Auth 标签配一遍，重复 |

```
POST /api/login?debug=1 HTTP/1.1        ← 方法 + URL + Params
Host: api.example.com                    ← Headers
Content-Type: application/json
Authorization: Bearer xxx                ← Authorization（本质也是头）
                                          ← 空行
{"user":"admin","pwd":"123"}             ← Body
```

- Postman 不是另一种发请求的方式；它把「一次性命令」变成「可保存、可复用、可演示的资产」。 curl 解决"这一次怎么发"，Postman 解决"这 50 条怎么管理、怎么重复跑、怎么给别人看"。
- 不是「Postman 把 curl 拆成块」，而是「curl 是这些块拼起来的结果」—— 你在 Postman 里填的每一块，最后都被拼成一条命令行。
- Postman 给我的不是“更省事的 curl”，而是“能留下来的请求”。 一条命令发完就没了；一条 Collection 里的请求，明天还在、能改、能复用、能被批量执行。

### 1.2 Code 按钮：把界面配置翻译成 curl（贴一条）

**输入：GET https://api.github.com**

#### 我改的地方

- a：什么都不改
- b：在headers里加上X-Test
- c：在headers里加上加上X-Test但是取消勾选框
- d：在Params里加上q=postman

#### curl 里多了什么

- a：`curl --location 'https://api.github.com'`
- b：多了一行 `--header`，完整命令是：
  
  ```bash
  curl --location 'https://api.github.com' \
  --header 'X-Test: 1'
  ```

- c：`curl --location 'https://api.github.com'`
- d：`curl --location 'https://api.github.com?q=postman'`

#### 证明

- a：为什么只有一行？ 因为我什么都没配 —— 没有头、没有参数、没有 body。 界面上那六个标签，只有填了内容才会出现在 curl 里。
- b：多了一行 --header。 这就是“Headers 标签 → -H”的证据。
- d：Params 没有变成参数，它直接进了 URL。 印证了1.1 那条：Params 就是 URL 的 query。

## 二、Request 五块

### 2.1 Params 就是 URL（文字说明）

**实验：双向验证**

| 我做 | 界面反应 |
| --- | --- |
| Params 里填 `q = postman` | URL 栏变成 `...?q=postman` |
| 反过来，直接在 URL 栏写 `?q=postman` | Params 标签自动出现一行 `q = postman` |

**结论：Params 不是"额外的参数"，它就是 URL 的 query —— 同一个东西的两种编辑方式。**

**所以两件事能推出：**

1. 改 Params 时，你其实在改 URL（不是"另外加了个参数"）
2. URL 编码（空格 → `%20`、中文 → `%E4%B8%AD`）会在 **URL 栏**可见；Params 里看到的是解码前的原样

**测试视角**：测"参数边界"时，改 Params 和改 URL 等价；但要**看真实的编码结果，看 URL 栏**。

### 2.2 Body 四种类型 → Content-Type

| Postman 里选 | 自动加的 Content-Type | 什么时候用 |
| --- | --- | --- |
| none | 不加 | GET 请求（没有体） |
| form-data | multipart/form-data | 文件上传 |
| x-www-form-urlencoded | application/x-www-form-urlencoded | 传统表单（a=1&b=2） |
| raw → JSON | application/json | 现代接口，90% 的情况 |
| raw → XML / Text | text/xml / text/plain | 少见 |
| binary | application/octet-stream | 上传二进制文件 |

### 2.3 我的 httpbin POST 回显（贴 json / headers / method 三个字段）

**输入**

```
方法：POST
URL：https://httpbin.org/post
Body：raw → JSON
      {"user":"admin","pwd":"123"}
```

**输出**

```
{
    "args": {},
    "headers": {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Length": "28",
        "Content-Type": "application/json",
        "Host": "httpbin.org",
        "Postman-Token": "bd755355-d2fa-4e4a-ab1e-ccde4232ecba",
        "User-Agent": "PostmanRuntime/2.15.0"
    },
    "method": "POST",
    "origin": "14.155.x.x",
    "url": "https://httpbin.org/post",
    "data": "{\"user\":\"admin\",\"pwd\":\"123\"}",
    "files": {},
    "form": {},
    "json": {
        "pwd": "123",
        "user": "admin"
    }
}
```

| 字段 | 说明什么 |
| --- | --- |
| json | 服务器成功解析出了你的 JSON |
| headers.Content-Type | 你实际发出去的 Content-Type |
| method | 服务器收到的确实是 POST |

## 三、Authorization 与 Cookie

### 3.1 Auth 标签 = 自动写一个头（切到 Headers 截图）

**输入**

```
方法：POST
URL：https://httpbin.org/post
Authorization：Bearer Token，Token = mytoken123
```

**Headers新增**

| Key | Value |
| --- | --- |
| Authorization | Bearer mytoken123 |

### 3.2 实验：不带 token 401 / 带 token 200（贴两次响应）

**专门测鉴权的端点：https://httpbin.org/bearer**

#### 第 1 步：不带凭证

**输入**

```
方法：GET
URL：https://httpbin.org/bearer
Authorization：No Auth
```

**输出**

```
401 Unauthorized
（空 body，0 B）
```

#### 第 2 步：带凭证

**输入**

```
方法：GET
URL：https://httpbin.org/bearer
Authorization → Bearer Token → Token 填：mytoken123
```

**输出**

```
200 OK
{
    "authenticated": true,
    "token": "mytoken123"
}
```

#### 第 3 步：故意改错 token

| 改法 | 预期 |
| --- | --- |
| Token 填空 | 401 |
| 换成 Basic Auth | 401（类型不匹配） |
| 去掉 `Bearer` 前缀 | 401（格式不完整） |

- httpbin 只校验"有没有 Bearer 凭证、格式对不对"，不校验值。
- 真实世界里"只检查 token 存在、不检查有效性"是高危缺陷： 攻击者随便编一个 token 就能进。 测试的方法就是：拿一个无效但格式合法的 token 去请求，看它是否放行。

### 3.3 Cookie：Postman 会/不会自动带

#### 第 1 步：让服务器种一个 Cookie

```bash
GET https://httpbin.org/cookies/set?session=abc123
```

**但Postman实际完成了两跳**

**第一跳输出**

```
:status: 302
access-control-allow-credentials: true
access-control-allow-origin: *
access-control-expose-headers: Retry-After, RateLimit, RateLimit-Policy
content-length: 223
content-type: text/html; charset=utf-8
location: /cookies
set-cookie: session=abc123; Secure; Path=/
x-content-type-options: nosniff
date: Mon, 09 Nov 2026 04:17:00 GMT
```

- 没有定位到，然后自动重定向完成第二跳

**第二跳输出**

```
:status: 200
access-control-allow-credentials: true
access-control-allow-origin: *
access-control-expose-headers: Retry-After, RateLimit, RateLimit-Policy
content-length: 47
content-type: application/json
x-content-type-options: nosniff
date: Mon, 09 Nov 2026 04:17:00 GMT
```

#### 第 2 步：看 Postman 有没有存

| 名称 | 值 |
| --- | --- |
| Name | session |
| Value | abc123 |
| Domain | httpbin.org |

#### 第 3 步：再发一次

**输入**

```bash
GET https://httpbin.org/cookies
```

**输出**

```
{
    "cookies": {
        "session": "abc123"
    }
}
```

### 3.4 三种 401 的区别

| 场景 | 服务器在说 | 怎么造 |
| --- | --- | --- |
| 没带凭证 | 你没证明你是谁 | No Auth |
| 凭证过期 | 你证明过，但过期了 | 用一个过期的 token |
| 凭证类型错 | 你用的是 Basic，我要 Bearer | 类型选错 |

### 3.5 Authorization 标签支持什么

| Type | 它做的事 | 什么时候用 |
| --- | --- | --- |
| No Auth | 不加任何凭证 | 公开接口 |
| Bearer Token | 加 Authorization: Bearer \<token> | JWT / 常见 Token |
| Basic Auth | 加 Authorization: Basic base64(user:pwd) | 老系统、内部接口 |
| API Key | 加自定义头，如 X-API-Key: xxx | 第三方开放平台 |
| OAuth 2.0 | 走完整授权流程 | 微信 / GitHub 第三方登录 |

## 四、Collection 与环境变量

### 4.1 为什么要 Collection

| 需求 | 单条请求 | Collection |
| --- | --- | --- |
| 存哪 | 发完就没了 | 左侧栏，永久保存 |
| 能共享吗 | ❌ | ✅ 导出成 JSON，发给别人 |
| 能批量跑吗 | ❌ | ✅ Runner（周三学） |
| 能复用配置吗 | ❌ | ✅ 变量、Auth 继承 |

### 4.2 三种变量的作用域与优先级

| 类型 | 作用域 | 什么时候用 |
| --- | --- | --- |
| Global | 全局，所有 Collection | 极少用（容易污染） |
| Environment | 当前选中的环境 | 常用：dev / test / prod |
| Collection | 这个 Collection 内 | 该集合专用的值 |
| Local | 一次运行 | 脚本临时用 |

- 优先级：Local > Data > Environment > Collection > Global（越具体越优先）。

### 4.3 我的环境变量配置（baseUrl / token）

| Variable | value |
| --- | --- |
| baseUrl | `https://httpbin.org` |
| token | mytoken123 |

### 4.4 切换 baseUrl 的实验结果

**输入{{baseUrl}}/get 的输出**

```
{
    "args": {},
    "headers": {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Authorization": "Bearer mytoken123",
        "Cookie": "session=abc123",
        "Host": "httpbin.org",
        "Postman-Token": "eed626ff-4de5-41a1-8460-8d7676ea9262",
        "User-Agent": "PostmanRuntime/2.15.0"
    },
    "method": "GET",
    "origin": "14.155.x.x",
    "url": "https://httpbin.org/get"
}
```

**输入 https://postman-echo.com/get 的输出**

```
{
    "args": {},
    "headers": {
        "host": "postman-echo.com",
        "authorization": "Bearer mytoken123",
        "accept-encoding": "gzip, br",
        "accept": "*/*",
        "user-agent": "PostmanRuntime/2.15.0",
        "postman-token": "e8c14e1c-a6dc-4a73-b83e-ea1c694dffd7",
        "x-forwarded-proto": "https",
        "cookie": "__cf_bm=***; _cfuvid=***; sails.sid=***"
    },
    "url": "https://postman-echo.com/get"
}
```

#### 换 baseUrl 的坑

- 换服务器后如果大量 404，先怀疑：**两边的路径前缀是不是一样**
- httpbin /get → postman-echo /get 都能 200，但 /bearer 只有 httpbin 有
- 所以"变量切换成功"和"请求能通"是两件事

## 五、响应与断言

### 5.1 响应区四标签

| 标签 | 看什么 |
| --- | --- |
| Body | 响应体：Pretty（格式化）/ Raw / Preview |
| Cookies | 服务器种的 Cookie |
| Headers | 响应头（Content-Type、Set-Cookie、Location…） |
| Test Results | 断言的执行结果（PASS / FAIL） |

- 日常排查顺序：先看状态码 → 再看 Headers 里的 Content-Type → 最后看 Body。

### 5.2 我写的第一条断言 + Test Results 文字描述

**断言**

```
pm.test("状态码是 200", function () {
    pm.response.to.have.status(200);
});
```

**Test Results 文字描述**

- 切到 Test Results，看到`passed 状态码是 200`，其中`passed`为绿底白字。

### 5.3 故意让它失败的结果

**断言**

```
pm.test("状态码是 200", function () {
    pm.response.to.have.status(404);
});
```

**Test Results 文字描述**

- 切到 Test Results，看到`failed 状态码是 200 | AssertionError: expected response to have status code 404 but got 200`，其中`failed`为红底白字。

## 六、断言的写法

**写法 A：快捷断言（只能断言状态码/头，但很短）**

```
pm.response.to.have.status(200);
pm.response.to.be.json;
pm.response.to.have.header("Content-Type");
```

**写法 B：通用断言（能断言任何东西，底层是 Chai）**

```
pm.expect(实际值).to.eql(期望值);        // 深比较
pm.expect(实际值).to.be.a('string');     // 类型
pm.expect(实际值).to.be.above(0);        // 大于
pm.expect(实际值).to.be.below(500);      // 小于
pm.expect(实际值).to.not.be.empty;       // 非空
pm.expect(实际值).to.include("abc");     // 包含
pm.expect(对象).to.have.property('token'); // 有某属性
```

**六条实用模板**

```
// 1. 状态码
pm.test("状态码 200", () => {
    pm.response.to.have.status(200);
});

// 2. 返回的是 JSON
pm.test("返回 JSON", () => {
    pm.response.to.be.json;
});

// 3. 字段存在且非空
pm.test("有 token", () => {
    const body = pm.response.json();
    pm.expect(body.data.token).to.be.a('string').and.not.empty;
});

// 4. 具体值
pm.test("用户名正确", () => {
    pm.expect(pm.response.json().user).to.eql("admin");
});

// 5. 类型
pm.test("id 是数字", () => {
    pm.expect(pm.response.json().id).to.be.a('number');
});

// 6. 响应时间
pm.test("响应小于 500ms", () => {
    pm.expect(pm.response.responseTime).to.be.below(500);
});
```

- 原则一：一条 pm.test 只断言一件事
- 原则二：断言要穿透到业务层

## 七、自检 10 题

| # | 问题 | 一句话回答 |
| --- | --- | --- |
| 1 | Postman 的五个区块分别对应报文哪一块 | 方法+URL：请求行；Params：URL的query；Headers：请求头；Body：请求体；Authorization：自动生成的请求头 |
| 2 | Params 和 URL 栏是什么关系 | Params是URL的query |
| 3 | 选了 raw 但没选 JSON，会发生什么 | 会导致明明输入了参数却弹400 |
| 4 | Auth 标签配了 Bearer，Headers 里还要手动加吗 | 不用，会导致重复，服务器会行为不确定 |
| 5 | 为什么会出现"登录了却 401"，Cookie 相关的原因是什么 | Cookie 的 Domain / Path 不匹配；Cookie 过期；接口用的是 Bearer Token，而没配 Auth |
| 6 | 三种 401 怎么区分 | 第一种：没有登录；第二种：登录完凭证过期了；第三种：凭证格式不对 |
| 7 | 环境变量有哪四种作用域，优先级如何 | 当次，这个集合内，环境，全局；Local > Data > Environment > Collection > Global |
| 8 | 为什么要把 baseUrl 抽成变量 | 方便在环境之间的切换 |
| 9 | 没有断言的接口测试，算自动化吗 | 不算，断言是自动化的眼睛 |
| 10 | Code 按钮有什么用 | 把当前设置拼成curl |

## 八、还没搞懂的

- 无

## 附：一个查清的问题

**为什么401的`body`是空的**

- Response Size = Headers 331 B + Body 0 B。
- 333 B 全是响应头，所以 `pm.response.json()` 必然抛 JSONError。

## 九、今日 10 题

- Q008 | httpbin 的 /bearer 为什么任意 token 都 200 | 它只校验格式不校验值，是"假鉴权"
- Q009 | 怎么测出"只验格式不验身份"的接口 | 拿一个无效但格式合法的 token 去请求
- Q010 | Basic Auth 的 401 是因为密码错吗 | 不是，是类型不匹配（端点要 Bearer）
- Q011 | `pm.response.json()` 在 401 响应上报 JSONError 是为什么 | 失败响应的 body 可能不是 JSON，解析会抛异常
- Q012 | 断言"响应里不能有 X"该怎么写 | 用 `pm.response.text()` 做子串检查，别用 `json()`
- Q013 | `pm.response.json().data.token` 报 undefined 是为什么 | 这个接口根本不返回 token，字段不存在
- Q014 | 断言该怎么确定字段路径 | 先看响应 Body 的实际 JSON，再按结构写
- Q015 | `.not.be.empty` 遇到 undefined 为什么报错 | 要先 `.to.be.a('string')` 再 `.not.empty`
- Q016 | 为什么 401 的响应 body 是空的 | 安全上不泄露失败原因，框架默认只给状态码
- Q017 | `pm.response.json()` 报 JSONError 怎么排查 | 先看 Response Size 里 Body 是不是 0，再看 Content-Type

> 已并入 `题库/QA-索引.md`

## 十、需要背诵并记忆

- Postman 的五个区块分别对应报文哪一块