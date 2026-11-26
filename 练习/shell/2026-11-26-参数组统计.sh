#!/bin/bash
LOG=/tmp/p32.out
grep -oE '::test_[a-zA-Z0-9_]+\[[^]]*\]' "$LOG" \
| sed 's/^:://; s/\[.*//' \
| sort | uniq -c | awk '{print $2 ":" $1 "组"}'

total=$(grep -oE '::test_[a-zA-Z0-9_]+\[[^]]*\]' "$LOG" | wc -l)
if [ "$total" -eq 0 ]; then
    echo "没有任何参数组，测试可能根本没跑" >&2
    exit 1
fi
exit 0