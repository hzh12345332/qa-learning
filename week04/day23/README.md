# Day 23 ｜ Python 回炉 ①：文件 / 异常 / JSON

产出：

| 文件 | 内容 |
|---|---|
| `01-Python文件异常JSON笔记.md` | 笔记主体：文件 / 异常 / JSON / 综合脚本 |
| `scripts/01_file_demo.py` | B1：写文件 + 逐行读 + `xxd` 验证换行 |
| `scripts/02_exception_demo.py` | B2：制造三种异常，看 `type(e).__name__` |
| `scripts/03_json_demo.py` | B3：`dumps` / `ensure_ascii` / `indent` / 存盘读回 |
| `scripts/report.py` | B4 + B5：读配置 → 跑用例 → 写报告（含三种坏情况） |
| `data/config.json` | 输入：`baseUrl` / `timeout` / `endpoint` |
| `data/users.csv` | 输入：3 行测试数据（`userId` / `expected`） |

> `data/` 里的 `report.json`、`out.json`、`demo.txt` 是**运行产物**，被 `.gitignore` 挡住，不入库。
> 判断标准：**删掉它别人还能跑 → 产物；不能 → 输入。**

## 今天搞清的五点

1. **`def` 只是登记，调用才执行**：函数体在定义时整段跳过，形参在调用时才有值
2. **`os.path.join` 只拼字符串**：不检查、不创建；真正动文件的是 `open()`
3. **`except: pass` 最危险**：出错当没发生，后面会报一个完全无关的错
4. **`else` 里的异常不会被 `except` 抓**：这是它和"写在 try 末尾"的唯一区别
5. **`indent` 只改格式不改数据**：所以改了 indent，`back == d` 还是 `True`

## 备注（今天的坑）

- **`NameError: name 'json' is not defined`** —— 忘了 `import json`。**报错信息直接给了答案**
- **`NameError: name 'sys' is not defined`** —— 手册骨架漏了 `import sys`，自己补的
- **GBK 默认编码**：Windows 上"不写 encoding"和"写 `gbk`"是同一个错，**真正的区别在 Linux**
- **`PermissionError` 写 `report.json`** —— 文件被 VS Code 占用，关掉标签页就好；**不是代码错**
- **自定义异常不会自动生成**：必须手动 `raise` 或用 `raise ... from` 包装，漏了 `except ConfigError` 就抓不到
- **`open(..., "w")` 会清空原文件** —— 用错一次数据就没了

## 加练（Shell）

- 题目：磁盘空间告警 → `练习/shell/2026-11-16-check-disk.sh`
- 结果：✅ 跑通，本机 C 盘 91% 触发 WARN，退出码 1
- 卡在哪：shebang 写成全角 `！`，`./` 跑失败，`bash` 跑成功 —— 用 `xxd` 才发现

## 明天

**Day 24：类与继承 / 模块 / 包**

> 今天写的 `load_config` / `run_case` / `main` 三个函数，明天会变成"一个类"。
> **今晚想一个问题**：如果 `report.py` 要支持 dev / test / prod 三个**环境**，你会怎么改？
> 明天用类来解决它。
