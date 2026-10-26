# Day 8 ｜ Linux 基础

> 日期：2026-10-26 ｜ 环境：Ubuntu 22.04（云服务器）

## 一、我敲过的命令（按用途分组）

| 命令 | 解决什么问题 | 我踩过的坑 |
| --- | --- | --- |
| `ls -la` | 看目录详情含隐藏文件 | 一开始不知道 -a 才显示 .ssh |
| `tail -f` | 实时跟踪日志 | 忘了 Ctrl+C 退出会卡住 |
| `cd /var/log` | 进入文件位置 | 第一次没搞清绝对位置和相对位置的区别 |
| `less /etc/services` | 用分页器以只读方式翻阅 /etc/services | 按esc想退出 |
| `find / -name "*.conf" 2>/dev/null \| head -5` | 屏蔽find / 全盘搜会报一堆 Permission denied。 | 只是屏蔽了所有错误返回，不是解决 |
| tail -f 和 tail -n 20 | 要一个能结束的结果 → -n；要持续观察 → -f | 没分清二者的区别 |

## 二、管道与重定向（我理解的核心）

（写清 > >> 2>&1 2>/dev/null 四者的区别，各配一个我实际跑过的例子）

- \>是覆盖，把原内容替换成新输入的内容，原内容消失

    1.输入`echo "A" > /tmp/a.txt` 2.输入`cat /tmp/a.txt` 3.文件中显示A
    4.输入`echo "Hello" > /tmp/a.txt` 5.输入`cat /tmp/a.txt` 6.文件中显示Hello

- \>>是追加写入，在原内容后加入新写入的内容，原内容依旧存在

    1.输入`echo "World" >> /tmp/a.txt`  2.输入`cat /tmp/a.txt`3.文件中显示Hello和World

- 2>&1把 stderr 合并到 stdout，stderr是给人看的，stdout是机器可读的。不加2>&1就只在终端上显示，加了会被写在文件里，可以被机器读取

- 2>/dev/null把错误信息指向一个黑洞，在终端上不进行显示

## 三、8 个组合命令的实测结果

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


## 四、还没搞懂的

- echo、-E、-o、-c、sort、uniq -c分别代表什么意思，在命令里有什么作用
- 是不是应该背一些Linux常用的命令
- 如何大致判断一串字符在命令中起到什么作用
