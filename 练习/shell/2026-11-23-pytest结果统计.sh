#!/bin/bash
LOG=/tmp/pytest.out
p=$(grep -c "PASSED" "$LOG")
f=$(grep -c "FAILED" "$LOG")
echo "PASSED: $p  FAILED: $f"
if [ "$f" -gt 0 ]; then
    exit 1
fi
exit 0