# Day 8 ｜ Linux 基础

> 日期：2026-10-26 ｜ 环境：Ubuntu 22.04（云服务器）

## 一、我敲过的命令（按用途分组）

| 命令 | 解决什么问题 | 我踩过的坑 |
| --- | --- | --- |
| `ls -la` | 看目录详情含隐藏文件 | 一开始不知道 -a 才显示 .ssh |
| `cd /var/log` | 进入文件位置 | 第一次没搞清绝对位置和相对位置的区别 |
| `cd .. && pwd` | 进入文件位置 | 绝对位置无论在哪里都可以进入对应文件的位置，相对路径只能进入该路径中的文件位置 |
| `less /etc/services` | 用分页器以只读方式翻阅 /etc/services | 按esc想退出 —— 正确的是按 **q** 退出 |
| `find / -name "*.conf" 2>/dev/null \| head -5` | 屏蔽find / 全盘搜会报一堆 Permission denied。 | 不加 2>/dev/null 会刷屏几百行，看不清结果 |
| `tail -f` | 要持续观察 → -f | 没分清和`tail -n 20`的区别 |
| `tail -n 20` | 要一个能结束的结果 → -n | 没分清和`tail -f`的区别 |
| `du -sh /var/log` | 看某个目录占了多少 | 需要和`df -h`进行区分 |
| `df -h` | 看整个文件系统还剩多少 | 需要和`du -sh /var/log`进行区分 |

## 二、管道与重定向（我理解的核心）

- \>是覆盖，把原内容替换成新输入的内容，原内容消失

    1.输入`echo "A" > /tmp/a.txt` 2.输入`cat /tmp/a.txt` 3.文件中显示A
    4.输入`echo "Hello" > /tmp/a.txt` 5.输入`cat /tmp/a.txt` 6.文件中显示Hello

- \>>是追加写入，在原内容后加入新写入的内容，原内容依旧存在

    1.输入`echo "World" >> /tmp/a.txt`  2.输入`cat /tmp/a.txt`3.文件中显示Hello和World

- 2>&1 把 stderr（fd2）合并到 stdout（fd1）：fd1 放正常**输出**结果，fd2 放**错误**输出结果

  ```bash
  命令 > file            # stdout 进文件，stderr 仍然打到终端
  命令 > file 2>&1       # stdout 进文件，stderr 也指向 file
  命令 2>/dev/null       # stderr 丢掉，stdout 正常显示
  ```

  **2>&1 的价值**：把错误信息也捕获进文件。
  记法：0 进 / 1 正常 / 2 错误。

- 2>/dev/null把错误信息指向一个黑洞，在终端上不进行显示

## 三、10 个组合命令的实测结果

- grep -c ERROR /root/qa-lab/logs/app.log

    输出：61

- grep -oE '\[(INFO|WARN|ERROR)\]' /root/qa-lab/logs/app.log | sort | uniq -c
  
    输出：61 [ERROR]
    65 [INFO]
    74 [WARN]

- grep ERROR /root/qa-lab/logs/app.log | head -3

    输出：2026-10-26 15:42:39 [ERROR] request_1 handled

    2026-10-26 15:42:39 [ERROR] request_2 handled

    2026-10-26 15:42:39 [ERROR] request_11 handled

- grep -v INFO /root/qa-lab/logs/app.log | head -5

    输出：2026-10-26 15:42:39 [ERROR] request_1 handled

    2026-10-26 15:42:39 [ERROR] request_2 handled

    2026-10-26 15:42:39 [WARN] request_3 handled

    2026-10-26 15:42:39 [WARN] request_5 handled

    2026-10-26 15:42:39 [WARN] request_6 handled

- grep ERROR /root/qa-lab/logs/app.log > /root/qa-lab/data/errors.txt

- wc -l /root/qa-lab/data/errors.txt

    输出：61 /root/qa-lab/data/errors.txt

- echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] manual append" >> /root/qa-lab/data/errors.txt
- tail -2 /root/qa-lab/data/errors.txt

    输出：2026-10-26 15:42:40 [ERROR] request_199 handled

    2026-10-26 16:20:35 [ERROR] manual append

- wc -l /root/qa-lab/logs/*.log

    输出：200 /root/qa-lab/logs/app.log

- du -sh /root/qa-lab/* | sort -rh

    输出：16K     /root/qa-lab/logs

    8.0K    /root/qa-lab/data

    4.0K    /root/qa-lab/scripts

    4.0K    /root/qa-lab/backup


## 四、目录结构

| 目录 | 放什么 |
| --- | --- |
| /etc | 配置文件 |
| /var/log | 日志 |
| /home | 普通用户家目录 |
| /root | root用户（管理员）家目录 |
| /tmp | 临时文件 |
| /opt | 第三方软件 |

```bash
file /dev/null
# 输出：/dev/null: character special (1/3)

ls -l /proc/1/exe
# 输出：lrwxrwxrwx 1 root root 0 Oct 25 19:49 /proc/1/exe -> /usr/lib/systemd/systemd
```

## 五、包管理与帮助系统

- **已安装包数量**：`apt list --installed | wc -l` → 输出 737 个
- **查看某命令帮助**：`ls --help | head -20`，或 `man ls`（按 q 退出）
- **真实系统日志**：`/var/log/syslog` 共 2557 行

查最近 10 条错误：
```bash
grep -inE 'error|fail' /var/log/syslog | tail -n 10
```
输出：
```
1114:Oct 25 19:49:44 iZwz9cnlz9teh2ihx7sn84Z udisksd[777]: failed to load module mdraid: libbd_mdraid.so.2: cannot open shared object file: No such file or directory
1117:Oct 25 19:49:44 iZwz9cnlz9teh2ihx7sn84Z udisksd[777]: Failed to load the 'mdraid' libblockdev plugin
1193:Oct 25 19:50:52 iZwz9cnlz9teh2ihx7sn84Z kernel: [   79.877382] AliSecGuard: module verification failed: signature and/or required key missing - tainting kernel
1266:Oct 25 19:54:37 iZwz9cnlz9teh2ihx7sn84Z systemd[1]: Starting Download data for packages that failed at package install time...
1268:Oct 25 19:54:37 iZwz9cnlz9teh2ihx7sn84Z systemd[1]: Finished Download data for packages that failed at package install time.
1582:Oct 25 19:59:33 iZwz9cnlz9teh2ihx7sn84Z snapd[9811]: stateengine.go:171: state ensure error: decode new commands catalog: context deadline exceeded (Client.Timeout or context cancellation while reading body)
1633:Oct 25 20:00:45 iZwz9cnlz9teh2ihx7sn84Z udisksd[20118]: failed to load module mdraid: libbd_mdraid.so.2: cannot open shared object file: No such file or directory
1634:Oct 25 20:00:45 iZwz9cnlz9teh2ihx7sn84Z udisksd[20118]: Failed to load the 'mdraid' libblockdev plugin
2555:Oct 26 19:55:01 iZwz9cnlz9teh2ihx7sn84Z systemd[1]: Starting Download data for packages that failed at package install time...
2557:Oct 26 19:55:01 iZwz9cnlz9teh2ihx7sn84Z systemd[1]: Finished Download data for packages that failed at package install time.
```

## 六、命令的解剖结构

从左往右读一条命令，每一段都有固定角色：

```
grep -oE 'pattern' app.log | sort | uniq -c > out.txt
 ①    ②      ③        ④     ⑤   ⑥      ⑦  ⑧    ⑨
```

| 序号 | 片段 | 角色 | 判断依据 | 作用 |
| --- | --- | --- | --- | --- |
| ① | `grep` | **命令**（动词） | 第一个词 | 干什么 |
| ② | `-oE` | **选项**（怎么干） | `-` 开头 | `-o` 只输出匹配部分；`-E` 用扩展正则 |
| ③ | `'pattern'` | **参数 1** | 引号包起来 | 搜索的模式 |
| ④ | `app.log` | **参数 2** | 不带 `-`，文件名 | 对谁干（在哪个文件里搜） |
| ⑤ | `\|` | **管道** | 竖线 | 把左边输出交给右边，**到这里"分句"** |
| ⑥ | `sort` | **命令** | 管道后重新开始 | 排序 |
| ⑦ | `uniq` | **命令** | | 合并相邻重复行 |
| ⑧ | `-c` | **选项** | `-` 开头 | 在每行前面加出现次数 |
| ⑨ | `> out.txt` | **重定向** | `>` / `>>` | 把最终输出写进文件 |

### 三个判断技巧

1. **看第一个词** —— 一定是命令
2. **看 `-` 开头** —— 是选项（`-o` 短选项、`--output` 长选项）
3. **看 `|`** —— 管道是"分句符"，后面重新开始算

### 验证某一段作用的方法：控制变量法

一次只删掉一段，对比输出怎么变：

```bash
grep -oE '\[(INFO|WARN|ERROR)\]' app.log | sort | uniq -c     # 原样：61 [ERROR] / 65 [INFO] / 74 [WARN]
grep -oE '\[(INFO|WARN|ERROR)\]' app.log | sort | uniq        # 去掉 -c：只剩级别，没有次数:[ERROR]\[INFO]\[WARN]
grep    -E '\[(INFO|WARN|ERROR)\]' app.log | sort | uniq -c   # 去掉 -o：整行各算一次，次数全变 1
grep -o    '\[(INFO|WARN|ERROR)\]' app.log | wc -l            # 去掉 -E：| 变成字面量，匹配 0 行
```

```mermaid
flowchart LR
    A["① grep<br/>命令"] --> B["② -oE<br/>选项"]
    B --> C["③ 'pattern'<br/>参数1"]
    C --> D["④ app.log<br/>参数2"]
    D --> E{"⑤ 管道"}
    E --> F["⑥ sort<br/>命令"]
    F --> G["⑦ uniq -c<br/>命令+选项"]
    G --> H["⑧ > out.txt<br/>重定向"]
```

## 七、还没搞懂的

- chmod 755 为什么是三个数字？
- ps aux 的 aux 各是什么
- /proc 目录是什么？
