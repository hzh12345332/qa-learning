#!/usr/bin/env bash
set -euo pipefail
log=${1:-access.log}
awk '{print $8}' "$log" | sort | uniq -c | sort -rn | awk '{print $2, $1}'