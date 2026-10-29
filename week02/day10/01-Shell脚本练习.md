# Day 10 ｜ Shell 脚本

## 一、骨架

### 1.1 shebang 为什么必须第一行

- #！这两个字符告诉内核：后面这个程序来解释这个文件
- #！/bin/bash写死路径
- #！/usr/bin/env bash会去PATH里面找bash（换机器会更稳）
- 必须是文件的第一个字节，前面有空格、空行、注释都不行。
- 为什么必须写：不写的话，./script.sh 会 fallback 到 /bin/sh 去解释， 而 /bin/sh 在 Ubuntu 上是 dash —— `[[ ]]`、数组、`$(( ))` 的某些写法在 dash 里直接报错。 这类报错极其难查，因为它只在"别人用 sh 跑你的脚本"时出现。

### 1.2 bash / ./ / source 三种执行方式的区别（表格 + 实验 1 输出）

| 方式 | 需要x位吗 | 在哪个shell里 | 变量会停留在当前终端上吗 |
| --- | --- | --- | --- |
| bash script.sh | 不需要 | 新起一个 bash（子 shell） | 不会 |
| ./script.sh | 需要 | 新起一个进程（按 shebang 决定） | 不会 |
| source script.sh 或 . script.sh | 不需要 | 当前 shell 本身 | 会 |

**后果**

1. `source` 会把变量污染到你的终端里，而且脚本里的 exit 会直接关掉你的终端窗口
2. 所以 chmod +x 只对 ./script.sh 这种写法有意义 —— 用 bash script.sh 跑没 x 位也能跑（昨天的实验 1 已经证过一次）
3. 改完 ~/.bashrc 要用 source 才立即生效，因为 bash ~/.bashrc 只是开了个新 shell 跑完就退

| 命令 | 输出 | 观察 |
| --- | --- | --- |
| ls -l env.sh | -rw-r--r-- 1 root root 79 Oct 28 09:11 env.sh | 读取到env.sh的详细信息 |
| bash env.sh | 脚本里 GREETING=from-script | 直接运行脚本env.sh |
| echo "终端里: ${GREETING:-（空）}" | 终端里: （空） | 检查终端里没有存储变量 |
| ./env.sh | -bash: ./env.sh: Permission denied | 没有执行权限 |
| chmod +x env.sh && ./env.sh | 脚本里 GREETING=from-script | 给env.sh加上执行权限，并且运行成功 |
| echo "终端里: ${GREETING:-（空）}" | 终端里: （空） | ./env.sh运行变量不会停留在终端 |
| source env.sh | 脚本里 GREETING=from-script | 运行成功 |
| echo "终端里: $GREETING" | 终端里: from-script | 变量停留在终端上 |

- 同一份脚本，三种跑法，变量去向完全不同。判断标准只有一个：是不是新起了一个 shell。

### 1.3 标准骨架

```
#!/usr/bin/env bash
set -uo pipefail          # 具体用哪几个，第 4 节讲

# 用法: ./demo.sh <参数>
name="${1:-默认值}"

echo "hello, ${name}"
```

## 二、变量与引号

### 2.1 赋值规则与 ${}

| 规则 | 示例 |
| --- | --- |
| 等号两边不能有空格 | name=qa |
| 会被当成"执行名为 name 的命令（赋值不能这样写） | name = qa |
| 值里有空格必须加引号 | name="qa lab" |
| 算术 | count=$((1 + 2)) |
| 数组 | items=(a b c) |
| 取第二个元素（下标从 0 开始） | echo "${items[1]}" |
| 全部元素 | echo "${items[@]}" |

- 引用的两种写法：$name 和 ${name}。能用花括号就用 —— 因为 $name.txt 会被理解成变量 name.txt，而 ${name}.txt 才正确。

### 2.2 三种引号（表格）

| 类型 | 使用场景 | 例子 |
| --- | --- | --- |
| 单引号 | 给 awk / sed / find 原样传程序 | awk '{print $1}' /etc/hostname |
| 双引号 | 99% 的场合都该用它 | dir="/root/qa-lab/logs" |
| 不加引号 | 只在想“拆成多个词”时用 | for u in $list; do |

**例子：name="qa lab"**

| 类型 | 命令 | 结果 |
| --- | --- | --- |
| 单引号 | printf '[%s]\n' '$name' | [$name] |
| 双引号 | printf '[%s]\n' "$name" | [qa lab] |
| 不加引号 | printf '[%s]\n' $name | [qa]/[lab] |

- 一句话结论：变量和命令替换永远加双引号；要传给别的程序的程序文本用单引号。

### 2.3 $@ / $* / "$@" / "$*" 四格表 + 我的实测结果

**假设执行 ./args.sh "a b" c（两个参数：第一个本身含空格）**

| 写法 | 会得到 |
| --- | --- |
| "$@" | 两个参数：a b、c |
| $@ | 先合并再按空格切 → a、b、c 三个 |
| "$*" | 一个字符串：a b c |
| $* | a、b、c 三个 |

- 不加引号时，$@ 和 $* 几乎总是等价的（都是“先展开、再按 IFS 分词”）。 两者的真正差别只在加了引号之后
- "$@" → 每个参数独立
- "$*" → 合成一个字符串
- "$#" 是参数个数

**以quote4.sh ab "c d"e为例的实测结果**

| 命令 | 结果 |
| --- | --- |
| "$@" | [ab][c de] |
| $@ | [ab][c][de] |
| "$*" | [ab c de] |
| $* |  [ab][c][de] |

### 2.4 位置参数与特殊变量（含 $? 与 128+信号 的换算）

| 变量 | 含义 | 例子 |
| --- | --- | --- |
| $0 | 脚本自己的名字 | ./run.sh |
| $1 $2 … | 第 1、2 个参数 |  |
| $# | 参数个数 | ./x.sh a b → 2 |
| "$@" | 所有参数（独立） |  |
| $? | 上一条命令的退出码 | 0 = 成功 |
| $$ | 当前 shell 的 PID |  |
| ${1:-默认} | 参数为空时用默认值 | 最常用 |
| ${1:?错误信息} | 参数为空就报错退出 | 参数校验神器 |

### 2.5 命令替换

- now=$(date +%F)          # ✅ 推荐
- 嵌套/引号判断口诀：$( ) 里面是一个全新的命令上下文，它自己的引号自己负责。
- echo "结果是: $(echo "里面也能用引号")"   # ✅ 外层双引号、内层双引号，互不干扰
- 同一个变量，加不加引号会得到不同的参数个数 —— 这就是"分词"。

## 三、退出码与错误处理

### 3.1 退出码对照表

| 退出码 | 含义 |
| --- | --- |
| 0 | 成功（只有 0 是成功，其它全是失败） |
| 1 | 一般性错误 |
| 2 | 用法错误 / 参数不对 |
| 126 | 找到了但不可执行（没 x 位） |
| 127 | 命令不存在（拼写错误最常见） |
| 130 | 被 Ctrl+C 中断（128+2） |
| 137 | 被 kill -9 杀掉（128+9） |
| 143 | 被 kill（TERM）终止（128+15） |

### 3.2 ; / && / || 的区别

| 写法 | 含义 |
| --- | --- |
| cmd1 ; cmd2 | 无论前面成不成功，都执行后面 |
| cmd1 && cmd2 | 前面成功才执行后面（短路） |
| cmd1 \|\| cmd2 | 前面失败才执行后面（兜底） |

### 3.3 set -e 的四个不生效位置

| 位置 | 为什么不生效 |
| --- | --- |
| if cmd; then的条件 | 条件本来就是在测"成不成功" |
| cmd1 && cmd2 的左边 | 左侧失败是允许的（短路逻辑） |
| ! cmd | 取反后算成功 |
| while cmd 的条件 | 条件本来就是在测"成不成功" |

- 管道只看最后一个命令：grep ERROR x.log \| wc -l —— 即使 grep 没匹配到，wc 也成功 → set -e 不触发。 所以要加 `set -o pipefail`，让管道里任何一个失败都算失败
- `set -e` 不管子 shell 内部：( false; echo x ) 里的行为要单独看
- 想"允许它失败"要显式写：cmd || true（比如 grep -c 无匹配时返回 1）

### 3.4 e / u / pipefail 各防什么

| 开关 | 防什么 | 什么时候用 |
| --- | --- | --- |
| set -e | 出错了还继续跑 | 部署、构建、任何"一步错后面全白费"的脚本 |
| set -u | 变量名打错 → 变成空字符串 → 静默做错事 | 几乎总是该开 |
| set -o pipefail | 管道中间的命令失败被吞掉 | 脚本里有管道就开 |

- set -euo pipefail     # 常用组合，写在第二行
- 什么时候不该用 `-e`：写的健康检查脚本 —— 它必须把 5 个 URL 全跑完再汇总，不能第一个失败就退出。 这就是"不能无脑用"的真实例子

### 3.5 实验 3 的 A/B/C/D 四组结果

| 编号 | 区别 | 结果 |
| --- | --- | --- |
| A | 没有set -e | 开始/我还在跑 ← 危险/A 退出码=0 |
| B | 加上set -e | 开始/B 退出码=1 |
| C | 管道陷阱（-e抓不到） | 0/C 还在跑 ← pipefail 没开/C 退出码=0 |
| D | 加 pipefail | 0/D 退出码=1 |

- C 和 D 的差别只有一行 pipefail，但一个是"静默放过"，一个是"当场停下"。

## 四、判断与分支

### 4.1 [ ] 的四个空格

| 结果 | 例子 |
| --- | --- |
| 正确 | if [ "$a" = "x" ]; then |
| 报错（把[$a当成命令） | if [$a = "x"]; then |
| 报错（把"x"]粘成一个词，显示misssing） | if [ "$a" = "x"]; then |
| 静默恒真 | if [ "$a"="x" ]; then 或 if [[ $a=x ]]; then |

- [ 是命令，所以它和它的参数之间必须有空白

### 4.2 判断速查表

| 类型 | 写法 | 说明 |
| --- | --- | --- |
| 字符串相等 | [ "$a" = "$b" ] | = 两边必须有空格 |
| 字符串不等 | [ "$a" != "$b" ] |  |
| 空 | [ -z "$a" ] | zero |
| 非空 | [ -n "$a" ] |  |
| 数值 | [ "$n" -eq 0 ] -ne -lt -le -gt -ge | 不能用 > <（会被当成重定向！） |
| 文件存在 | [ -f path ] | 是普通文件 |
| 目录存在 | [ -d path ] |  |
| 存在即可 | [ -e path ] | 文件或目录都算 |
| 可执行 | [ -x path ] |  | 
| 非空文件 | [ -s path ] | size > 0 |

- 注意：数值比较别用 `>`：[ $a > $b ] 会被 shell 解析成"把输出重定向到文件 b"，结果默默创建了一个文件。要么用 -gt，要么用 (( a > b ))。

### 4.3 为什么数值不能用 > <

- 会被shell解析成重定向，结果就是创建了一个文件

### 4.4 case

```
if [ "$code" = "200" ]; then
  echo "OK"
elif [ "$code" = "000" ]; then
  echo "连不上"
else
  echo "异常: $code"
fi

case "$1" in
  start)  echo "启动" ;;
  stop)   echo "停止" ;;
  *)      echo "用法: $0 {start|stop}"; exit 2 ;;
esac
```

## 五、循环与逐行读文件

### 5.1 for

| 写法 | 来源 | 是否启动外部进程 | 使用场景 |
| --- | --- | --- | --- |
| for i in 1 2 3 | 写死的字面量 | 否 | 几个固定项 |
| for u in "${urls[@]}" | 数组 | 否 | 一组 URL / 文件名（最常用） |
| for i in $(seq 1 5) | 命令输出 | 是（seq） | 数量由别的命令决定 |
| for ((i=1;i<=5;i++)) | 自己数 | 否 | 计数、步长、倒序 |

**1-5的三种写法（不需要启动seq）**

- for i in {1..5}; do echo "$i"; done        # 1 2 3 4 5
- for i in {1..10..3}; do echo "$i"; done    # 1 4 7 10（步长 3）
- for i in {5..1}; do echo "$i"; done        # 5 4 3 2 1（倒序）

### 5.2 while IFS= read -r 三件套

```
while IFS= read -r line; do
  echo "行内容: $line"
done < "$file"
```

| 部分 | 防什么 | 不写的后果 |
| --- | --- | --- |
| IFS= | 不修剪行首行尾的空白 | 行首缩进被吃掉（日志、YAML、代码都受影响） |
| read | 读一整行 | 没有 read 就不是"逐行读"，循环根本跑不起来 |
| -r | 不解释反斜杠 | \n、\t 被转义成真实字符，路径里的 \ 被吃掉 |
| < "$file" | 让循环在当前 shell 里跑 | 用管道的话循环在子 shell，变量改了读不到 |

### 5.3 for in $(cat) 的三宗罪 + 实验 5 对比输出

| 罪 | 后果 |
| --- | --- |
| 1. 按空白分词 | 一行里有空格就被拆成多个"行" |
| 2. 会做通配符展开 | 内容里有 *、? 会被展开成文件名 |
| 3. 一次把所有内容读进内存 | 大文件直接吃满内存 |

| 命令 | 结果 | 观察 |
| --- | --- | --- |
| for line in $(cat tricky.txt); do echo "[$line]"; done | 见a1 | 把每个元素都拆成独立的一行了 |
| echo "--- while IFS= read -r ---"while IFS= read -r line; do echo "[$line]"; done < tricky.txt | 见a2 | 输出正确的内容 |
| cat tricky.txt \| while IFS= read -r line; do n=$((n+1)); done | 管道版计数：0 | 管道右侧在子shell里执行，出了子shell变量就没了 |
| while IFS= read -r line; do n=$((n+1)); done < tricky.txt | 管道版计数：3 | 重定向了 |

**a1：**

```
[indented]
[line]
[has]
[space]
[here]
[star]
[a.sh]
[b.sh]
[c.sh]
[d.sh]
[env.sh]
[quote4.sh]
[tricky.txt]
[here]
[last-no-newline]
```

**a2：**
```
--- while IFS= read -r ---
[  indented line]
[has space here]
[star * here]
```

- for 版输出的行数和内容都对不上；管道版计数是 0；重定向版才对。

### 5.4 管道 while 变量丢失 + 三种解法

- 重定向

```
count=0
while read -r line; do count=$((count+1)); done < app.log
echo "行数: $count"
```

- 进程替换

```
while read -r line; do count=$((count+1)); done < <(cat app.log)
```

- lastpipe（bash 4.2+，要求非交互且 job control 关闭）

```
shopt -s lastpipe
```

- 别把要改的变量放在管道右边。 用 < file 或 < <(...)。

## 六、三个实战脚本

### 脚本 1：URL 健康检查 check_urls.sh

| 代码 | 运行输出 | 问题 |
| --- | --- | --- |
| ./check_urls.sh; echo "退出码=$?" | 见a1 | curl 会先打印状态码，再收完整个响应体。 |

**a1：**
```
OK   https://www.saucedemo.com/  (200)
FAIL https://www.saucedemo.com/inventory.html  (000000)
FAIL https://www.saucedemo.com/cart.html  (404000)
FAIL https://www.saucedemo.com/checkout-step-one.html  (404000)
FAIL https://www.saucedemo.com/不存在的页面  (400)
-----------------------------
成功 1 个 / 失败 4 个
失败清单:
  - https://www.saucedemo.com/inventory.html -> 000000
  - https://www.saucedemo.com/cart.html -> 404000
  - https://www.saucedemo.com/checkout-step-one.html -> 404000
  - https://www.saucedemo.com/不存在的页面 -> 400
退出码=1
```

**修改后命令：**
```
# ① 换掉 urls 列表（4 个真 200 + 1 个故意 404）
urls=(
  "https://www.saucedemo.com/"
  "https://www.saucedemo.com/index.html"
  "https://www.saucedemo.com/robots.txt"
  "https://www.baidu.com/"
  "https://www.saucedemo.com/nope.html"
)

# ② for 循环里的取状态码改成三行
  raw=$(curl -s -4 -o /dev/null -m "$timeout_sec" -w "%{http_code}" "$u" 2>/dev/null || true)
  code="${raw:0:3}"
  case "$code" in [0-9][0-9][0-9]) ;; *) code="000" ;; esac
```

**修改后结果**

```
OK   https://www.saucedemo.com/  (200)
OK   https://www.saucedemo.com/index.html  (200)
OK   https://www.saucedemo.com/robots.txt  (200)
OK   https://www.baidu.com/  (200)
FAIL https://www.saucedemo.com/nope.html  (404)
-----------------------------
成功 4 个 / 失败 1 个
失败清单:
  - https://www.saucedemo.com/nope.html -> 404
退出码=1
```

### 6.2 check_logs.sh（app.log vs app2.log 两次输出）

**修改前命令 ：**

```
#!/usr/bin/env bash
set -euo pipefail

log="${1:?用法: $0 <日志文件> [阈值]}"
threshold="${2:-3}"

if [ ! -f "$log" ]; then
  echo "错误: 文件不存在 -> $log" >&2
  exit 2
fi

total=$(wc -l < "$log")
echo "文件: $log"
echo "总行数: $total"

# grep -c 无匹配时返回 1，用 || true 兜底（set -e 下必须写）
err_count=$(grep -c ERROR "$log" || true)
err_count=${err_count:-0}
echo "ERROR 行数: $err_count"

echo "--- 按小时分布 ---"
grep ERROR "$log" 2>/dev/null | awk '{print $3}' | cut -d: -f1 | sort | uniq -c | sort -rn || true

echo "--- Top ${threshold} 高频错误 ---"
grep ERROR "$log" 2>/dev/null | sed 's/.*ERROR//' | sort | uniq -c | sort -rn | head -"$threshold" || true

if [ "$err_count" -gt 0 ]; then
  echo "结果: 发现 ${err_count} 条 ERROR，需要关注"
  exit 1
fi
echo "结果: 没有 ERROR"
```

**修改前结果：**

```
./check_logs.sh: line 4: 1: 用法: ./check_logs.sh <日志文件> [阈值]
退出码=1
```

- 原因：${1:?...} 的意思是：如果 $1 没给，就把消息打到 stderr 并退出。它的报错格式是固定的。
- 错误：我的日志是 日期 时间 [级别] 消息，小时在 $2，我取的 $3 拿到的是 [ERROR]

**改动的命令：**

```
echo "--- 按小时分布 ---"
grep ERROR "$log" 2>/dev/null | awk '{print $2}' | cut -d: -f1 | sort | uniq -c | sort -rn || true

echo "--- Top ${threshold} 高频错误 ---"
grep ERROR "$log" 2>/dev/null | sed 's/.*\[ERROR\] //' | sort | uniq -c | sort -rn | head -"$threshold" || true
```

**改动后结果：**

```
文件: /root/qa-lab/logs/app2.log
总行数: 24
ERROR 行数: 18
--- 按小时分布 ---
      6 11
      6 10
      6 09
--- Top 3 高频错误 ---
      9 connection refused to db
      6 timeout after 30s
      3 500 internal server error
结果: 发现 18 条 ERROR，需要关注
```

### 6.3 check_sys.sh

**命令：**

```
#!/usr/bin/env bash
set -uo pipefail

disk_threshold=80
mem_min_mb=200

disk_used=$(df -P / | awk 'NR==2 {gsub("%","",$5); print $5}')
mem_avail=$(free -m | awk '/^Mem:/ {print $7}')

echo "根分区使用率: ${disk_used}%  (阈值 ${disk_threshold}%)"
echo "可用内存: ${mem_avail} MB  (下限 ${mem_min_mb} MB)"

alert=0
if [ "${disk_used:-0}" -gt "$disk_threshold" ]; then
  echo "告警: 磁盘使用率超过 ${disk_threshold}%" >&2
  alert=1
fi
if [ "${mem_avail:-0}" -lt "$mem_min_mb" ]; then
  echo "告警: 可用内存低于 ${mem_min_mb} MB" >&2
  alert=1
fi
exit "$alert"
```

**输出：**

```
根分区使用率: 17%  (阈值 80%)
可用内存: 453 MB  (下限 200 MB)
退出码=0
```

### 6.4 run-all.sh

**命令：**

```
#!/usr/bin/env bash
set -uo pipefail

cd "$(dirname "$0")"      # 保证从任何目录调用都能找到同级脚本
total=0
failed=0

for s in check_urls.sh check_logs.sh check_sys.sh; do
  case "$s" in
    check_logs.sh) args=(/root/qa-lab/logs/app2.log 3) ;;   # 用有 3 种错误的日志
    *)             args=() ;;
  esac

  total=$((total + 1))
  echo "=========== 运行 $s ==========="
  if bash "$s" "${args[@]}"; then
    echo ">>> $s 通过"
  else
    echo ">>> $s 失败 (退出码 $?)"
    failed=$((failed + 1))
  fi
done

echo "======================================"
echo "共 ${total} 个脚本，失败 ${failed} 个"
[ "$failed" -eq 0 ]
```

**输出：**

```
=========== 运行 check_urls.sh ===========
OK   https://www.saucedemo.com/  (200)
OK   https://www.saucedemo.com/index.html  (200)
OK   https://www.saucedemo.com/robots.txt  (200)
OK   https://www.baidu.com/  (200)
FAIL https://www.saucedemo.com/nope.html  (404)
-----------------------------
成功 4 个 / 失败 1 个
失败清单:
  - https://www.saucedemo.com/nope.html -> 404
>>> check_urls.sh 失败 (退出码 1)
=========== 运行 check_logs.sh ===========
文件: /root/qa-lab/logs/app2.log
总行数: 24
ERROR 行数: 18
--- 按小时分布 ---
      6 11
      6 10
      6 09
--- Top 3 高频错误 ---
      9 connection refused to db
      6 timeout after 30s
      3 500 internal server error
结果: 发现 18 条 ERROR，需要关注
>>> check_logs.sh 失败 (退出码 1)
=========== 运行 check_sys.sh ===========
根分区使用率: 18%  (阈值 80%)
可用内存: 472 MB  (下限 200 MB)
>>> check_sys.sh 通过
======================================
共 3 个脚本，失败 2 个
退出码=1
```

## 七、今天踩的坑（现象 → 原因 → 修法

| 现象 | 原因 | 修法 |
| --- | --- | --- |
| 脚本里 $1 变空 | heredoc 漏引号 → 写文件时就展开了 | 用 <<'EOF' |
| 退出码是 0 但中途失败过 | 退出码 = 最后一条命令 | 加 set -e 或最后 exit 1 |
| 日志全对但 Top3 没意义 | 日志只有一种错误消息 | 造 app2.log 制造多样性 |

## 八、五个问题（已搞懂）

- 重定向法怎么实现的

```
while read -r line; do echo "$line"; done < file      # 循环在【当前 shell】
cat file | while read -r line; do echo "$line"; done  # 循环在【子 shell】
```

  一句话：重定向 = 换个输入来源（同一间屋子）；管道 = 另开一间屋子。

- 错误码里面的128是什么？

正常退出码是 0–127，被信号杀死时拿不到"正常退出码"，所以用 128 以上表示"我是被信号干掉的，编号是 N-128"。这不是错误分类，是偏移量。

- 直接打命令和把命令添加进文件的区别是什么

| 维度 | 直接打 | 写进文件 |
| --- | --- | --- |
| 谁执行 | 交互式 shell（你） | 非交互式 shell（bash） |
| 能复用 | ❌ | ✅ |
| 能给别人/给机器跑 | ❌ | ✅（cron、CI、run-all.sh） |
| 执行前能 review | ❌ | ✅ |
| 出错能停 | ❌（你盯着看） | 需要 set -e 自己停 |

- 什么情况下推荐直接打命令，什么情况下推荐把命令添加进文件

判断标准只有一句：「这件事我明天还会做吗？」，会就写进文件，不会就直接打

- 常见的命令和含义

| 我要干什么 | 用哪个 |
| --- | --- |
| 看文件内容 | cat less head tail -f |
| 找东西 | grep（找内容）、find（找文件） |
| 看系统状态 | ps aux top df -h free -m ss -tulnp |
| 改权限 / 属主 | chmod chown |
| 文本加工 | awk sed cut sort uniq |
| 网络 | curl nc ping |
| 服务 | systemctl journalctl |
