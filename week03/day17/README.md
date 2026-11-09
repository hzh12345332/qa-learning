# Day 17 ｜ Postman 基础

产出：

| 文件 | 内容 |
|---|---|
| `01-Postman基础笔记.md` | 笔记主体：五个区块 ↔ 报文、Auth、Cookie、环境变量、第一条断言 |
| `postman/Day17 练习.postman_collection.json` | 导出的集合（4 条请求） |

## 今天搞清的四个点

1. **Postman 的五个区块，就是报文四块的表单版** —— Params 就是 URL 的 query，Authorization 就是自动帮你写一个头
2. **Auth 标签和 Headers 手写只能二选一** —— 两个都配会发出两个 `Authorization` 头
3. **Postman 自动管 Cookie，不管 Authorization** —— "登录了却 401"的头号原因
4. **环境变量让切换环境只改一处** —— `{{baseUrl}}` 从 httpbin 换到 postman-echo，URL 一个字没改

## 备注

- **Environment 文件不进仓库**：它含 token / 账号，哪怕只是练习值也不该养成习惯
- 导出的 Collection JSON 提交前**搜一遍 token**，有真实值就替换成 `{{token}}`
- 今天的产出是**练习级（⭐）**，还进不了产出雷达；**周五那套完整集合**才是 ⭐⭐⭐