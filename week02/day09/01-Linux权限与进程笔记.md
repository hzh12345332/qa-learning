# Day 9 ｜ Linux 进阶（权限 / 进程 / 服务 / 网络）

## 一、权限

### 1.1 权限串怎么读

| 位置 | 是什么 |
| --- | --- |
| 第一位 | 文件类型：`-`普通文件；`d`目录；`l`软连接；`c/b`设备 |
| 第二到第四位 | 属主 u（user/owner） |
| 第五到第七位 | 属组 g（group） |
| 第八到第十位 | 其他人 o（other） |

### 1.2 三类人 × 三种权限 = 4/2/1

| 权限串 | 数字 | 含义 | 用途 |
| --- | --- | --- | --- |
| -rwxr-xr-x | 755 | 属主全权，其他人可看可执行不可写 | 目录 |
| -rw-r--r-- | 644 | 属主可读写，其他人只可读 | 普通网页、日志 |
| -rw------- | 600 | 只有属主可读写 | 私钥、密码文件 |
| -rwx------ | 700 | 只有属主能进 | .ssh目录 |
| -rwxrwxrwx | 777 | 所有人全权 | 安全漏洞 |

| 位 | 字母 | 数值 | 对文件 | 对目录 |
| --- | --- | --- | --- | --- |
| 读 | r | 4 | cat可以看内容 | ls可以列出目录中的名字 |
| 写 | w | 2 | 能够修改内容 | 能在里面新建/删除/改名文件 |
| 执行 | x | 1 | 能作为程序运行 | cd可以进入、能访问里面已知名字的文件 |

一组三个权限相加：rwx = 4+2+1 = 7，r-x = 4+0+1 = 5，r-- = 4。 三组拼起来就是三位数：7 5 5。

### 1.3 我敲过的 chmod / chown 命令

| 命令 | 作用 | 我实际用它做了什么 |
| --- | --- | --- |
| chmod 755 hello.sh | 给与属主全权，其他人读和执行权 | 给hello.sh文件赋予属主全权，其他人读和执行权 |
| chmod 600 ~/.ssh/authorized_keys | 只给属主读写权 | 把密钥文件设置为只有属主可读写 |
| chmod +x hello.sh | 给所有人加执行权 | 给所有人加上hello.sh文件的执行权 |
| chmod u+x hello.sh | 只给u（属主）加执行权 | 给属主加上hello.sh的执行权 |
| chmod g-w file | 去掉g（属组）的写 | 把属组对file的写权去掉 |
| chown qa file | 改属主 | 把file的属主改成qa |
| chown qa:qa file | 同时改属主和属组 | 把file的属主和属组都改成qa |

### 1.4 特殊权限（只记结论）

| 位 | 数字 | 名字 | 例子 |
| --- | --- | --- | --- |
| 属主 x 位变 s | 4755 | SUID | /usr/bin/passwd（普通用户改密码时临时获得 root 权限） |
| 属组 x 位变 s | 2755 | SGID | 目录里新建的文件自动继承目录的属组 |
| 其他 x 位变 t | 1777 | Sticky | /tmp（谁都能建文件，但只能删自己的） |

```
ls -ld /tmp
# drwxrwxrwt  ← 最后的 t 就是 sticky
```

为什么 /tmp 是 1777" → 所有人都能建文件（777），但 sticky 保证你只能删自己建的，防止互删。
（小问题：特殊权限的数字也是算出来的吗？）

### 1.5 踩到的坑

1. 目录只有 `r` 没有 `x` → ls 能列出文件名，但 cd 进不去，也读不到任何文件内容（属性列显示成 ?）。
2. 目录只有 `x` 没有 `r` → 进得去，但 ls 报 Permission denied；只要你知道确切文件名，照样能打开它。
3. 文件自己 `-r--r--r--`（444，只读）也能被删除 —— 因为删除动作改的是目录，只要目录有 w 就行。这条能直接答"为什么只读文件也会被删"。

### 1.6 umask：755 和 644 是"默认"出来的

新建文件时没指定权限，系统却给了值 —— 因为有个 **umask（权限掩码）** 在按位清除权限。

| 对象 | 基础权限 | umask | 计算结果 | 实际 |
| --- | --- | --- | --- | --- |
| 文件 | 666（默认不给 x） | 022 | 666 & ~022 | **644 = rw-r--r--** |
| 目录 | 777 | 022 | 777 & ~022 | **755 = rwxr-xr-x** |

```bash
umask                     # 预期：0022
touch f1 && mkdir d1
ls -l f1                  # -rw-r--r--  = 644
ls -ld d1                 # drwxr-xr-x  = 755

umask 077                 # 只影响之后新建的东西
touch f2 && ls -l f2      # -rw-------  = 600
```

> **算法是"按位清除"，不是十进制减法**：`644 − 022 = 622` 是错的，正确是 `644 & ~022 = 644`。
> 只是 `666`、`777` 这两组恰好减法与按位结果相同，容易让人误以为是减法。

## 二、进程

### 2.1 ps aux 每列含义（表格）

| 列 | 含义 | 什么时候用 |
| --- | --- | --- |
| USER | 谁起的 | 排查"是不是权限不对" |
| PID | 进程号 | 杀进程、看 /proc/PID |
| %CPU / %MEM | 实时占用 | 找"谁把机器吃满了" |
| VSZ / RSS | 虚拟内存 / 实际物理内存（KB） | 找内存泄漏 |
| STAT | 状态 | 看进程是不是「僵尸」或「卡死」 |
| START / TIME | 启动时间 / 累计 CPU 时间 | 看是不是刚重启过 |
| COMMAND | 启动命令 | 看是哪个程序、带什么参数 |

| 字母 | 全称 | 作用 |
| --- | --- | --- |
| a | all | 显示所有用户的进程（不只你自己） |
| u | user-oriented | 显示用户/CPU/内存等详细列 |
| x | 无控制终端 | 显示没有终端的进程（守护进程） |

### 2.2 STAT 状态码

| 值 | 含义 |
| --- | --- |
| R | 正在运行或可运行 |
| S | 睡眠中（在等事件，绝大多数进程常态） |
| D | 不可中断睡眠（通常卡在磁盘 I/O，kill -9 都杀不掉） |
| Z | 僵尸进程（已结束但父进程没回收） |
| T | 已停止（被 Ctrl+Z 或 kill -STOP） |

后面再加字母：s = 会话首进程，l = 多线程，+ = 在前台进程组。

**找线程的写法**

| 命令 | 结果 |
| --- | --- |
| ps aux \| grep http.server | 最常用，但会把自己的 grep 也列出来 |
| ps aux \| grep http.server \| grep -v grep | 去掉自己 |
| pgrep -af http.server | 更干净：直接输出 PID + 命令行 |
| pgrep -a -f "python3 -m http" | -f 匹配完整命令行 |

`ps aux | grep 进程名` 会匹配到自己，这是经典坑。面试里被问"怎么查进程"，答出 grep -v grep 或 pgrep 会加分。

### 2.3 kill 的信号

| 信号 | 数字 | 含义 | 什么时候用 |
| --- | --- | --- | --- |
| SIGHUP | 1 | 挂断 | nohup 就是"忽略它"；也常用来让服务重载配置 |
| SIGINT | 2 | 中断 | 就是 Ctrl+C |
| SIGKILL | 9 | 强杀 | 不可被捕获，进程没机会做清理，可能留下脏数据 |
| SIGTERM | 15 | 终止 | 默认，可被捕获，进程能优雅退出（关连接、落盘） |
| SIGTSTP | 20 | 暂停 | 就是 Ctrl+Z |

| 命令 | 含义 |
| --- | --- |
| kill -l | 列出所有信号 |
| kill 1234 | 等于 kill -15 1234，先礼 |
| kill -9 1234 | 后兵（只有 kill 不掉时才用） |
| kill -0 1234 | 不真的杀，只检查进程存不存在（$? 为 0 表示存在） |

先 kill（TERM），等几秒，ps 确认还在，再 kill -9。 直接 `-9` 会跳过清理逻辑，对数据库、消息队列这类进程尤其危险。

### 2.4 & / Ctrl+Z / jobs / fg / nohup 的区别（本节核心）

- &是放到后台运行，立刻返回提示符，输出 [1] 1234（作业号 + PID）。默认 huponexit=off，exit 后作业通常存活；只有断网/关窗口才发 SIGHUP 带走它。
- Ctrl+Z是把前台的进程暂停，提示 [1]+ Stopped
- jobs是查看当前shell的后台和暂停作业。（如&或Ctrl+Z）
- bg %1是把暂停的作业放到后台继续跑
- fg %1是把后台的作业调回前台
- Ctrl+C是终止前台进程
- nohup = no hang up，忽略 SIGHUP

`> nohup.log 2>&1` = 标准输出和错误都写文件（不重定向的话，nohup 默认写 nohup.out）

>结尾 & = 放后台（少了它，nohup 也会占着终端）exit 是"我主动走的"，bash 悄悄结束；断网是"我被踢出去的"，bash 会挨个通知作业。 所以 & 的行为不稳定 —— 这本身就是它不能上生产的原因

>三者的关系要能说清：& 只是"后台"，nohup 只是"免疫 HUP"，两个一起用才是"关掉终端还在"。

### 2.5 /proc 是什么（见正文 3.6 节）

- /proc 是内核内存里的一个"假文件系统"，每个 PID 对应一个目录，进程自己的一切都挂在那儿

| 命令 | 作用 |
| --- | --- |
| pgrep -af http.server | 假设拿到 PID 12345 |
| ls /proc \| head -20 | 全是数字目录 = 全是进程 |
| cat /proc/12345/cmdline \| tr '\0' ' '; echo | 完整启动命令（用 \0 分隔） |
| readlink /proc/12345/cwd | 这个进程的工作目录 |
| ls -l /proc/12345/fd | 它打开的每个文件 / socket |
| head -5 /proc/12345/status | 状态、内存、线程数 |

排障时 /proc/PID/fd 最有用：能看出一个进程到底占着哪些文件、哪些网络连接。 （lsof 本质上就是把这一堆 fd 整理成人类可读的表格。）
ps、top、ss、lsof 全都是从 /proc 里读数据拼出来的。

## 三、服务

### 3.1 systemctl 命令表

| 命令 | 作用 | 一句话记住 |
| --- | --- | --- |
| systemctl status 服务名 | 看状态 | 第一眼看这个 |
| systemctl start 服务名 | 现在启动 | 只管这一次 |
| systemctl stop 服务名 | 现在停止 | 开机还会起来 |
| systemctl restart 服务名 | 重启 | 改了配置之后用 |
| systemctl reload 服务名 | 重载配置 | 不中断服务（不是所有服务都支持） |
| systemctl enable 服务名 | 开机自启 | 下次开机才生效，不等于现在启动 |
| systemctl disable 服务名 | 取消开机自启 | 现在还在跑 |

**查service 名字**

```
systemctl list-units --type=service --state=running    # 正在运行的
systemctl list-unit-files --type=service --state=enabled  # 开机自启的
systemctl list-units --type=service --all              # 全部（含停止的）
```

### 3.2 start 和 enable 的区别

`start` vs `enable` ： start = 现在跑；enable = 以后开机自动跑。 常见事故：systemctl start nginx 之后重启机器，服务没了 —— 因为没 enable。 反过来：enable 了但从没 start，当前就是停的。 两步都要：systemctl enable --now 服务名（= enable + start）。

### 3.3 journalctl 怎么按服务看日志

| 命令 | 作用 |
| --- | --- |
| journalctl -u ssh | 只看 ssh 的日志 |
| journalctl -u ssh -n 50 | 最后 50 行 |
| journalctl -u ssh -f | 实时跟踪（等价于 tail -f） |
| journalctl -xe | 最近错误（排障第一命令） |
| journalctl -p err -b | 次开机以来的 error 级别 |

>和 Day 8 的 `tail -f /var/log/syslog` 的区别： /var/log/syslog 是所有服务混在一起的流水；journalctl -u 服务名 才是按服务过滤。 排障时先用 journalctl -u，找不到再去 syslog 里 grep。

### 3.4 我查清的 3 个服务

| 服务 | 干什么 | 停掉会怎么样 |
| --- | --- | --- |
| cron | 定时任务 | 所有 crontab 任务不再执行 |
| rsyslog | 写 /var/log/syslog 等日志文件 | 日志只进 journal，/var/log 里没有 |
| unattended-upgrades | 自动装安全更新 | 系统不再自动打补丁 |

## 四、网络

### 4.1 四层诊断顺序

| 层级 | 命令 | 作用 |
| --- | --- | --- |
| 第 3 层 网络层 | ping | 通不通？延迟多少？ |
| 第 4 层 传输层 | nc -zv | 这个端口开没开？ |
| 第 7 层 应用层 | curl -v | 服务返回了什么？（状态码、响应头、报错体） |
| 旁路 本机 | ss -tulnp | 本机到底在监听哪个地址、哪个端口 |

排障顺序铁律：从下往上。 不要一上来就 curl，先确认 ping 通不通、端口开没开 —— 否则你会对着一个"服务正常但防火墙没放行"的问题查半天代码。

### 4.2 ss -tulnp 五个参数

| 参数 | 作用 |
| --- | --- |
| -t | TCP |
| -u | UDP |
| -l | 只看 listening（监听中） |
| -n | 显示数字端口，不做服务名反解（8080 而不是 http-alt） |
| -p | 显示进程（需要 root，否则看不到程序名） |

### 4.3 curl -v 输出怎么看（请求头 / 响应头）

1. - Trying 47.119.188.156:443... / * Connected to ... → 握手过程
2. > GET / HTTP/2 / > Host: ... / > User-Agent: ... → 请求头（> 是发出）
3. < HTTP/2 200 / < content-type: text/html → 响应头（< 是收到）

### 4.4 ping 通不代表服务通（为什么）

- 根本原因：协议层级不同
- ping使用的是ICMP协议，工作在OSI模型的网络层（第三层）
- 而服务（网页、API、SSH等）使用的是TCP或UDP协议，工作在传输层（第四层）
- ping通”仅仅证明网络路径通畅，目标主机的操作系统有响应

## 五、五个实验记录

### 实验 1：权限实验（45 min）

>A 部分：root 下的 x 位实验（15 min）

> **前提（必须先知道）**：你现在是 `root`。**root 会绕过 r/w 检查** —— 读任何文件都不受
> `r` 限制，所以用 root 做读写实验**永远看不到 Permission denied**。
> **但 `x` 位例外**：root 要执行一个文件，也必须有至少一个 `x` 位。
> 所以 A 部分只能在 root 下做「x 位」实验；目录的 `r` / `x` 实验必须切到普通用户（B 部分）才做得出来。

| 命令 | 实际输出 | 观察 |
| --- | --- | --- |
| cd /root/qa-lab | 无 | 进入/root/qa-lab下 |
| cat > hello.sh <<'EOF' | 无 | 创造一个叫hello的脚本 |
| ls -l hello.sh | -rw-r--r-- | hello.sh属主有读写权，其他人只可读 |
| ./hello.sh | -bash: ./hello.sh: Permission denied | 没有hello.sh的执行权限 |
| bash hello.sh | hello, qa | 执行成功，bash 只需要读这个文件（它自己是有 x 的，执行的是 bash，不是脚本 |
| chmod +x hello.sh | 无 | 给所有人加上hello.sh的执行权限 |
| ls -l hello.sh | -rwxr-xr-x | 所有人多了hello.sh的执行权限 |
| ./hello.sh | hello, qa | 成功执行 |
| chmod 644 hello.sh | 无 | 把所有人改回644 |
| ./hello.sh | -bash: ./hello.sh: Permission denied | 没有hello.sh的执行权限 |
| chmod 700 hello.sh | 无 | 给属主全权，取消其他人的所有权限 |
| ls -l hello.sh | -rwx------ | hello.sh属主全权，其他人无任何权限 |
| ./hello.sh | hello, qa | 成功执行 |

>B 部分：建普通用户，做目录实验（30 min）

| 命令 | 实际输出 | 观察 |
| --- | --- | --- |
| `adduser --disabled-password --gecos "" qa` `id qa` | 见a1 | 创建了一个普通用户qa |
| usermod -aG sudo qa | 无 | 让 qa 能用 sudo |
| chown qa:qa /home/qa/lab | 无 | 只让 qa 拥有 lab 这一层，d1/d2 仍归 root |
| chmod 744 /home/qa/lab/perm/d1 | 无 | 给d1，744权限 |
| chmod 711 /home/qa/lab/perm/d2 | 无 | 给d2，711权限 |
| ls -ld /home/qa/lab/perm/d1 /home/qa/lab/perm/d2 | 见a2 | d1和d2分别有744权限和711权限 |
| su - qa | 见a3 | 从root切入qa |
| whoami | qa | 显示已经在qa中 |
| cd /home/qa/lab/perm | 无 | 进入/home/qa/lab/perm |
| ls d1 | a.txt | 显示出名字 |
| cd d1 | -bash: cd: d1: Permission denied | qa没有执行权限 |
| cat d1/a.txt | cat: d1/a.txt: Permission denied | qa没有执行权限到不了位置 |
| ls -l d1 | -????????? ? ? ? ? | 无法stat |
| cd d2 | 无 | 有执行权限所以成功进入 |
| ls | ls: cannot open directory '.': Permission denied | 没有读取权限所以显示不出来 |
| cat b.txt | secret | 知道名字所以读出来了 |

**a1：**

```
Adding user `qa' ...
Adding new group `qa' (1000) ...
Adding new user `qa' (1000) with group `qa' ...
Creating home directory `/home/qa' ...
Copying files from `/etc/skel' ...
uid=1000(qa) gid=1000(qa) groups=1000(qa)
```

**a2：**

```
drwxr--r-- 2 root root 4096 Oct 27 10:37 /home/qa/lab/perm/d1
drwx--x--x 2 root root 4096 Oct 27 10:38 /home/qa/lab/perm/d2
```

**a3：**

```
To run a command as administrator (user "root"), use "sudo <command>".
See "man sudo_root" for details.
```

1. 为什么 ls d1 成功而 cd d1 失败？

- ls d1因为有读取权限所以可以列出名字，cd d1因为没有执行权限所以失败。

1. 为什么 cat d2/b.txt 成功而 ls d2 失败？

- cat d2/b.txt因为有执行权限所以成功，ls d2因为没有读取权限所以失败

1. 回到 root，把 d1 改成 chmod 644 d1（连属主都没 x）再 su - qa 去 cd，会怎样？
  
- 会显示-bash: cd: d1: Permission denied。表示权限被拒绝

### 实验 2：进程与端口

| 命令 | 实际输出 | 观察 |
| --- | --- | --- |
| python3 -m http.server 8080 & | [1] 12345 | 起一个 HTTP 服务，作业号 1，PID 12345 |
| jobs | [1]+  Running    python3 -m http.server 8080 | 展示后端作业 |
| ps aux \| grep http.server \| grep -v grep | root       27419  0.0  1.0  27572 17880 pts/0    S    14:41   0:00 python3 -m http.server 8080 | 找出命令行里带 http.server 的进程（手工拼接） |
| pgrep -af "http.server" | 27419 python3 -m http.server 8080 | 找出命令行里带 http.server 的进程（专门工具） |
| ss -tulnp \| grep 8080 | tcp   LISTEN 0      5                 0.0.0.0:8080      0.0.0.0:*    users:(("python3",pid=27419,fd=3)) | 谁跟 8080 这个端口有关系 |
| lsof -i:8080 | COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME python3 27419 root    3u  IPv4 155891      0t0  TCP *:http-alt (LISTEN) | 谁跟 8080 这个端口有关系 |
| curl -I <http://127.0.0.1:8080> | 见b1 | 成功访问 |
| kill %1 | 无 | 用作业号杀死进程 |
| ss -tulnp \| grep 8080  ; echo "退出码=$?" | 退出码=1 | 验证进程被杀死 |
| jobs | 无 | 确认进程被杀死 |

**b1：**

```
HTTP/1.0 200 OK
Server: SimpleHTTP/0.6 Python/3.10.12
Date: Tue, 27 Oct 2026 07:11:25 GMT
Content-type: text/html; charset=utf-8
Content-Length: 488
```

### 实验 3：& vs nohup（30 min）

| 命令 | 实际输出 | 观察 |
| --- | --- | --- |
| python3 -m http.server 8081 & | [1] 27878 | 拉起服务 |
| ss -tulnp \| grep 8081 | tcp   LISTEN 0      5                 0.0.0.0:8081      0.0.0.0:*    users:(("python3",pid=27878,fd=3)) | 还在监听 |
| exit | 无 | 退出SSH |
| ssh root@47.119.188.156 | 无 | 重新登录SSH |
| pgrep -af "http.server 8081" | 27553 python3 -m http.server 8081 | 依旧存活 |
| curl -I <http://127.0.0.1:8081> | curl: (52) Empty reply from server | 活着但是不可用了 |
| nohup python3 -m http.server 8082 > /root/qa-lab/nohup.log 2>&1 & | [1] 27982 | nohup + 重定向，换一个端口 |
| ss -tulnp \| grep 8082 | tcp   LISTEN 0      5                 0.0.0.0:8082      0.0.0.0:*    users:(("python3",pid=27982,fd=3)) | 确认在监听 |
| exit | 无 | 退出SSH |
| ssh root@47.119.188.156 | 无 | 重新登录SSH |
| pgrep -af "http.server 8082" | 27982 python3 -m http.server 8082 | 进程依然存活 |
| curl -I <http://127.0.0.1:8082> | 见b2 | 进程依然可用 |

> **PID 核对**：起服务时是 `[1] 27878`，重登后 `pgrep` 却是 `27553` —— **PID 对不上，说明存活的是更早的残留进程**，
> 而不是我刚起的那个。排障时只要 PID 不一致，就要先怀疑"我打到旧进程上了"，再下结论。

**b2：**

```
HTTP/1.0 200 OK
Server: SimpleHTTP/0.6 Python/3.10.12
Date: Tue, 27 Oct 2026 07:54:17 GMT
Content-type: text/html; charset=utf-8
Content-Length: 781
```

**为什么 `exit` 后进程还活着、`curl` 却是 52？**

| 现象 | 发生了什么 |
| --- | --- |
| `pgrep` 还有 PID | 进程没死：`exit` 是优雅退出，bash 默认 `huponexit=off`，不通知后台作业（**断网/关窗口才会发 SIGHUP**，那时才死） |
| `curl: (52) Empty reply from server` | 进程活着，但 stdout/stderr 仍指向**已经消失的终端**。它一写访问日志就失败，连接被直接掐断 → 端口有人监听，却一句话回不出来 |

**两个必须分清的 curl 错误码**：

| 错误 | 含义 | 说明什么 |
| --- | --- | --- |
| `(7) Failed to connect` | TCP 层就没人接 | **没有进程在监听** |
| `(52) Empty reply from server` | TCP 连上了，对方一句话不说就挂断 | **有人监听但回不了包**（崩了、卡死、写日志失败） |

> 所以 `nohup` 的价值不只是"让进程活着"，而是"**活着且还能用**"——靠 `> nohup.log 2>&1` 给输出找了个新去处。
> 三件事缺一不可：`nohup`（免疫 HUP）+ 重定向（输出有新家）+ `&`（放后台）。

### 实验 4：服务管理（45 min）

| 命令 | 实际输出 | 观察 |
| --- | --- | --- |
| systemctl status ssh --no-pager | 见c1 | 查看服务状态 |
| systemctl is-enabled ssh | enabled | 开机自启已启用 |
| systemctl list-units --type=service --state=running \| head -20 | 见c2 | 20条正在运行中的服务 |
| journalctl -u ssh --since "30 minutes ago" --no-pager \| tail -30 | 见c3 | 显示了30分钟前的日志 |
| systemctl status cron --no-pager | 见3.4 | 定时任务守护进程，描述行就写了用途 |
| systemctl status rsyslog --no-pager | 见3.4 | 系统日志服务，日志写进 /var/log |
| systemctl status unattended-upgrades --no-pager | 见3.4 | 平时是 inactive(dead)，由 apt-daily.timer 触发才跑 —— 所以 c2 的运行列表里没有它 |

**c1：**

```
● ssh.service - OpenBSD Secure Shell server
     Loaded: loaded (/lib/systemd/system/ssh.service; enabled; vendor preset: enabled)
     Active: active (running) since Sun 2026-10-25 19:58:58 CST; 1 day 20h ago
       Docs: man:sshd(8)
```

**c2：**

```
 UNIT                        LOAD   ACTIVE SUB     DESCRIPTION
  aegis.service               loaded active running Aegis Service
  aliyun.service              loaded active running Aliyun Assist
  atd.service                 loaded active running Deferred execution scheduler
  chrony.service              loaded active running chrony, an NTP client/server
  cron.service                loaded active running Regular background program processing daemon
  dbus.service                loaded active running D-Bus System Message Bus
  fwupd.service               loaded active running Firmware update daemon
  getty@tty1.service          loaded active running Getty on tty1
  multipathd.service          loaded active running Device-Mapper Multipath Device Controller
  networkd-dispatcher.service loaded active running Dispatcher daemon for systemd-networkd
  packagekit.service          loaded active running PackageKit Daemon
  polkit.service              loaded active running Authorization Manager
  rsyslog.service             loaded active running System Logging Service
  serial-getty@ttyS0.service  loaded active running Serial Getty on ttyS0
  snapd.service               loaded active running Snap Daemon
  ssh.service                 loaded active running OpenBSD Secure Shell server
  systemd-journald.service    loaded active running Journal Service
  systemd-logind.service      loaded active running User Login Management
  systemd-networkd.service    loaded active running Network Configuration
```

**c3：**

```
Oct 27 19:05:34 iZwz9cnlz9teh2ihx7sn84Z sshd[28858]: Invalid user admin from 139.19.117.130 port 41048
Oct 27 19:05:34 iZwz9cnlz9teh2ihx7sn84Z sshd[28858]: userauth_pubkey: key type ssh-rsa not in PubkeyAcceptedAlgorithms [preauth]
Oct 27 19:05:43 iZwz9cnlz9teh2ihx7sn84Z sshd[28858]: Connection closed by invalid user admin 139.19.117.130 port 41048 [preauth]
Oct 27 19:13:41 iZwz9cnlz9teh2ihx7sn84Z sshd[28874]: error: kex_exchange_identification: client sent invalid protocol identifier ""
Oct 27 19:13:41 iZwz9cnlz9teh2ihx7sn84Z sshd[28874]: banner exchange: Connection from 23.111.14.186 port 50532: invalid format
Oct 27 19:33:00 iZwz9cnlz9teh2ihx7sn84Z sshd[28903]: error: kex_exchange_identification: Connection closed by remote host
Oct 27 19:33:00 iZwz9cnlz9teh2ihx7sn84Z sshd[28903]: Connection closed by 64.89.160.135 port 58000
```

### 实验 5：网络诊断四件套（45 min）

| 命令 | 实际输出 | 观察 |
| --- | --- | --- |
| ping -c 4 <www.baidu.com> | 见d1 | ping通了，没有丢包，延迟9.150ms |
| ping -c 4 47.119.188.156 | 见d2 | ping通了，没有丢包，延迟0.297ms |
| nc -zv 47.119.188.156 22 | Connection to 47.119.188.156 22 port [tcp/ssh] succeeded! | 成功链接到22端口 |
| nc -zv 47.119.188.156 3306 | connect to 47.119.188.156 port 3306 (tcp) failed: Connection timed out | 静默丢弃（安全组 DROP） |
| curl -s -o /dev/null -w "%{http_code} %{time_total}\n" <https://www.saucedemo.com> | 200 131.012830 | 查看到状态码和耗时 |

**d1：**

```
--- www.a.shifen.com ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3003ms
rtt min/avg/max/mdev = 9.137/9.150/9.162/0.011 ms
```

**d2:**

````
--- 47.119.188.156 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3053ms
rtt min/avg/max/mdev = 0.274/0.297/0.319/0.017 ms
````

## 六、综合演练：4 个人造故障

### 故障 A：权限不对

| 项 | 结果 |
| --- | --- |
| 现象 | -bash: ./run.sh: Permission denied （权限被拒绝） |
| 命令 | **输入**：ls -l run.sh，**输出**：-rw-r--r-- |
| 结论 | 属主、属组和其他人都没有执行权限 |
| 修改 | chmod +x run.sh |

### 故障 B：端口被占

| 项 | 结果 |
| --- | --- |
| 现象 | OSError: [Errno 98] Address already in use |
| 命令 | tcp   LISTEN 0      5                 0.0.0.0:8080      0.0.0.0:*    users:(("python3",pid=28869,fd=3))
| 结论 | 端口被占用 |
| 修改 | nohup python3 -m http.server 8081 > /dev/null 2>&1 & |

### 故障 C：绑错地址

| 项 | 结果 |
| --- | --- |
| 现象 | 本机 curl 127.0.0.1:8080 通，外部访问超时 |
| 命令 | ss -tulnp 看 Local Address 列：是 127.0.0.1:8080 而不是 0.0.0.0:8080 |
| 结论 | 只绑了回环地址，外部无法连接 |
| 修改 | 改成0.0.0.0 |

### 故障 D：安全组 / 防火墙

>未真实操作，仅为理论推测

| 项 | 结果 |
| --- | --- |
| 现象 | 服务在 0.0.0.0:8080 正常监听、本机 curl 通，本地电脑访问 <http://47.119.188.156:8080> 超时 |
| 命令 | 本地 nc -zv 47.119.188.156 8080 → 超时；服务器 ss -tulnp \| grep 8080 → 正常监听 |
| 结论 | 链路在云端被拦：阿里云安全组未放行 8080 |
| 修改 | 开放8080端口 |

## 七、服务起不来 / 访问不通，按这个顺序问

1. 我有没有权限执行它？            → ls -l、chmod、ls -ld 目录
2. 进程起来了吗？起来后还活着吗？    → ps aux / pgrep、journalctl -u、看日志
3. 它在监听吗？听在哪个地址？        → ss -tulnp
4. 外面进得来吗？                   → ping / nc / curl，再看云安全组

## 八、三个问题（已搞懂）

### 8.1 查清一个服务，查哪几个方面

| # | 问什么 | 命令 | 看哪个字段 |
| --- | --- | --- | --- |
| 1 | 它是什么 | `systemctl status x --no-pager` | 第一行 `名字 - 描述` |
| 2 | 它活着吗 | `systemctl is-active x` | active / inactive / failed |
| 3 | 开机会自启吗 | `systemctl is-enabled x` | enabled / disabled |
| 4 | 它用什么端口 | `ss -tulnp \| grep <Main PID>` | Local Address 列 |
| 5 | 配置在哪 | `systemctl cat x` | 单元文件路径 + `ExecStart=` |
| 6 | 为什么出错 | `journalctl -u x -n 50 --no-pager` | 最后 50 行 |

补充两条：

```bash
systemctl --failed                     # 一次列出所有 failed 的服务 ← 排障第一站
systemctl list-dependencies ssh        # 它依赖谁、谁依赖它（启动顺序问题）
```

> **一句话**：`status` 只给「描述 + 状态」两层，往下要靠 **Main PID**（接进程/端口）和 **journalctl**（查原因）自己接上。

### 8.2 `curl -v ... | head -40` 为什么超时

两个坑叠在一起：

1. **`head -40` 读满就退出** → curl 继续写会收到 `SIGPIPE`，退出码 **23（write error）**。这不是超时，但它把**报错信息截断了**，看不到真正原因。
2. **真的卡住**：阿里云 ECS 多数没有 IPv6 出口，而 DNS 会返回 AAAA 记录，curl **先试 IPv6，等连接超时才回退 IPv4**。

判断方法：看 `-v` 卡在哪一行（`*` 是过程，`>` 是发出，`<` 是收到）。

| 卡在 | 含义 | 处理 |
| --- | --- | --- |
| `* Trying 2606:...`（IPv6 地址） | IPv6 不通 | 加 `-4` 强制 IPv4 |
| `* Trying 47.x.x.x:443...` 之后无响应 | TCP 握手不回（跨境/被拦） | `--connect-timeout 5 -m 20` |
| `* TLS handshake` 卡住 | TLS 被干扰 | `-m 20` 复现，再试 `--tlsv1.2` |
| `HTTP/2 200` 之后慢 | 还在收响应体（`-o /dev/null` 也要收完） | 正常，用 `-m` 兜底 |

```bash
# 看尾巴而不是开头，并强制 IPv4 + 超时
curl -4 -v -m 15 https://www.saucedemo.com -o /dev/null 2>&1 | tail -20
```

> **凡是可能连不上的命令都要给上限**：`curl -m`、`nc -w`、`ping -c`、`timeout`。

### 8.3 systemctl status 的输出怎么读

```
● ssh.service - OpenBSD Secure Shell server
↑①圆点颜色：绿=运行中 白=停止 红=failed
  ↑②单元名        ↑③描述 ← "它是干什么的"看这一行就够了

     Loaded: loaded (/lib/systemd/system/ssh.service; enabled; vendor preset: enabled)
             ↑④加载状态  ↑⑤单元文件位置        ↑⑥开机自启  ↑⑦发行版默认值

     Active: active (running) since Sun 2026-10-25 19:58:58 CST; 1 day 20h ago
             ↑⑧当前状态          ↑⑨何时变成这个状态         ↑⑩距今多久

   Main PID: 1234 (sshd)
             ↑⑪主进程号 ← 拿它去 ss / ps 继续查
```

**⑧ Active 的取值是排障第一判断点**：

| 值 | 意思 | 下一步 |
| --- | --- | --- |
| `active (running)` | 在跑 | 继续查端口/功能 |
| `active (exited)` | 一次性任务正常跑完 | 这类服务本来就不常驻，不是故障 |
| `inactive (dead)` | 没在跑 | `journalctl -u x -n 50` |
| `failed` | 启动失败 / 崩溃 | 同上，日志里必有原因 |
| `activating (auto-restart)` | 反复重启 | 常见于配置写错或端口被占 |

**⑥ 和 ⑦ 别搞混**：⑥`enabled` 是**我设的**开机自启（`systemctl enable` 改的是它）；⑦`vendor preset` 是 **Ubuntu 出厂**的建议值。而且 `enabled` **只说明"设了"，不代表"现在在跑"** —— 那要看 ⑧。

**实验 4 那三个服务怎么对应**：看 ③ 描述行就够了；想进一步确认，`systemctl cat` 看它 `ExecStart` 启动的到底是什么程序。

| 服务 | 描述行 |
| --- | --- |
| `cron` | Regular background program processing daemon（定时任务） |
| `rsyslog` | System Logging Service（把日志写进 /var/log） |
| `unattended-upgrades` | Unattended Upgrades（自动装安全更新） |

## 九、Day 10 还没搞懂的（预习）

> Day 10 是 Shell 脚本。下面三条是这条路线上最容易卡住的地方，明天带着问题去写脚本。

### 9.1 退出码：为什么脚本"出错了却继续往下跑"

单条命令失败（`$?` 非 0）之后，bash **默认不会停**，下一行照跑。

- 那 `set -e` 到底能让它停在哪，又为什么常被说"不能无脑用"？
- `set -euo pipefail` 三个开关分别防什么？
- `cmd1 && cmd2`、`cmd1 || cmd2`、`cmd1 ; cmd2` 的退出码怎么传递？

### 9.2 引号与参数：`$@` / `$*` / `"$@"` 到底差在哪

- 为什么 `"$@"` 通常是对的，而 `$@`（不加引号）和 `$*` 会出事？
- 变量不加引号时，"空格分词"和"通配符展开"会在什么时候咬人？
- `$(...)` 套引号、引号里再套命令替换，怎么判断哪一层被解释了？

### 9.3 逐行读文件：`for i in $(cat f)` 为什么是错的

- 文件名带空格、行首带缩进、末尾没换行时，`for` 循环会出什么错？
- `while IFS= read -r line` 里 `IFS=`、`read`、`-r` 各自在防什么？
- 管道里的 `while` 为什么会"改了变量却读不到"（子 shell 问题）？
