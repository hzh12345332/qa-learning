# Day 20 ｜ 抓包（DevTools + Fiddler）

产出：

| 文件 | 内容 |
|---|---|
| `01-抓包笔记.md` | 笔记主体：DevTools / 抓包原理 / Fiddler / 定位问题 / 手机抓包 |
| `scripts/fake-user.json` | AutoResponder 的假响应，把 `httpbin.org/get` 换成"用户不存在" |

> **抓包存证不进仓库**：HAR、`Copy as cURL` 出来的完整命令里都带 Cookie/Token，只留在本地。
> 要给人看就贴路径 + 状态码，截图前先打码。

## 今天搞清的五点

1. **没发 ≠ 失败**：列表里没有这条请求 = 前端没发；有请求但返回 5xx = 后端异常
2. **中间人不"破解"HTTPS**：工具用自签根证书把一条连接拆成两条，客户端的信任链终点是"我装的根"
3. **只有 `Tunnel` 没有 `GET` = 没解密**：流量到了 Fiddler，但证书或解密开关没生效
4. **TTFB 才是"慢在哪"**：实测 241ms 里 239ms 在等服务器，Content Download 只有 0.35ms
5. **责任划分**：4xx 找前端、5xx 找后端、200 但字段不对还是后端

## 备注

- **下载页卡在 reCAPTCHA**：Telerik 的表单依赖 Google reCAPTCHA，本机不通就点不动按钮 —— 换网络后成功
- **全局断点会先拦 `CONNECT`**：隧道那一步没有业务参数可改，要先 `Run to Completion` 才能拦到真正的 GET
- **`curl -x` 只抓到 CONNECT**：`-s` 把 `SEC_E_UNTRUSTED_ROOT` 吞了，Schannel 不认 Fiddler 证书 —— 用 `-sS` 看错误、`-k` 绕过
- **导入 Postman 后返回 304**：cURL 把 `If-None-Match` / `If-Modified-Since` 一起抄了过来，删掉这两个头才是"全新请求"
- **手机**：端口 8080 改 8888 才通；证书装好后能抓华为浏览器；App 还受 Android 7+ 和 pinning 限制
- **插曲**：`grs.dbankcloud.com` 用华为内部 CA 签证书，Windows 不认 —— 点 No 放弃该会话，不是自己配置的问题

## 明天第一件事

`week03/day17/postman/Day17 练习.postman_collection.json` → 挪到 `week03/postman/`，去掉 "Day17"。
今天导入的 `Github API` 那条一起放进去，当 M1 的"真实业务"素材。

## 本周还剩三天

| 日 | 内容 |
|---|---|
| 11/13 周五 | **产出：完整集合（M1 验收）** |
| 11/14 周六 | 缓冲 / 补漏 |
| 11/15 周日 | 休息 |
