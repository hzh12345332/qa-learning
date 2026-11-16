#!/usr/bin/env bash
usage=$(df -h / | awk 'NR==2 {gsub(/%/,"",$5); print $5}')
if [ "$usage" -gt 80 ]; then
    echo "WARN: 磁盘使用率 ${usage}%"
    exit 1
fi
echo "OK: ${usage}%"