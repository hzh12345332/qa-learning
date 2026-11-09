# -*- coding: utf-8 -*-
"""把各天笔记里的「今日 N 题」并入 题库/QA-索引.md

用法:
    python tools/sync_qa.py --dry     # 只看会改什么
    python tools/sync_qa.py           # 实际写入

笔记里的题行格式（第 4/5 段可省）:
    - Q008 | 问题 | 一句话答案
    - Q008 | 问题 | 一句话答案 | 🔁
    - Q008 | 问题 | 一句话答案 | 🔁 | §3.2

「展开」列 = 笔记所在目录名 + 可选小节，如 `day17 §3.2`。
"""
import re
import sys
import pathlib

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = pathlib.Path(__file__).resolve().parent.parent
QA = ROOT / "题库" / "QA-索引.md"
STATES = {"⬜", "🔁", "✅", "📦"}


def parse_entries():
    """扫描所有周目录下的逐日笔记，返回 {QID: (问题, 答案, 展开, 状态)}"""
    found = {}
    dup = []
    for note in sorted(ROOT.glob("week*/*/0*.md")):
        if note.name.upper().startswith("README"):
            continue
        day = note.parent.name
        lines = note.read_text(encoding="utf-8").split("\n")
        in_block = False
        for line in lines:
            if re.match(r"^#+\s*.*今日\s*\d+\s*题", line):
                in_block = True
                continue
            if in_block and line.startswith("#"):
                break
            if not in_block:
                continue
            m = re.match(r"^-\s*(Q\d+)\s*\|(.+)$", line.strip())
            if not m:
                continue
            qid = m.group(1)
            parts = [p.strip() for p in m.group(2).split("|")]
            q = parts[0] if parts else ""
            a = parts[1] if len(parts) > 1 else ""
            state = "⬜"
            sec = ""
            for p in parts[2:]:
                if p in STATES:
                    state = p
                elif p.startswith("§"):
                    sec = p
            ref = day + (" " + sec if sec else "")
            if qid in found:
                dup.append((qid, found[qid][2], ref))
            found[qid] = (q, a, ref, state)
    return found, dup


def load_index():
    if not QA.exists():
        return None
    text = QA.read_text(encoding="utf-8")
    lines = text.split("\n")
    start = None
    for i, ln in enumerate(lines):
        if ln.strip().startswith("| ID |"):
            start = i
            break
    if start is None:
        return None
    i = start
    block = []
    while i < len(lines) and lines[i].strip().startswith("|"):
        block.append(lines[i])
        i += 1
    return lines, start, i, block


def split_row(row):
    body = row.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    cells, cur, esc = [], "", False
    for ch in body:
        if esc:
            cur += ch
            esc = False
        elif ch == "\\":
            esc = True
            cur += ch
        elif ch == "|":
            cells.append(cur.strip())
            cur = ""
        else:
            cur += ch
    cells.append(cur.strip())
    return cells


def main():
    dry = "--dry" in sys.argv
    entries, dups = parse_entries()
    if not entries:
        print("没找到任何「今日 N 题」条目")
        return
    if dups:
        print("警告：重复的题号（后面的会覆盖前面的）：")
        for qid, a, b in dups:
            print("   %s  已有 %s / 又出现 %s" % (qid, a, b))

    idx = load_index()
    if not idx:
        print("读不到 %s 的索引表" % QA)
        return
    lines, start, end, block = idx
    head, sep, old_rows = block[0], block[1], block[2:]
    existing = {}
    for r in old_rows:
        c = split_row(r)
        if c and re.fullmatch(r"Q\d+", c[0]):
            existing[c[0]] = c

    added, updated = 0, 0
    for qid, (q, a, ref, state) in entries.items():
        # 笔记只给到文件级时，不覆盖索引里已经更精确的小节指针
        old = existing.get(qid)
        if old and "§" in old[3] and "§" not in ref:
            ref = old[3]
        new = [qid, q.replace("|", "\\|"), a.replace("|", "\\|"), ref, state]
        if qid in existing:
            if existing[qid][:5] != new:
                existing[qid] = new
                updated += 1
        else:
            existing[qid] = new
            added += 1

    keys = sorted(existing, key=lambda k: int(k[1:]))
    rows = ["| " + " | ".join(existing[k][:5]) + " |" for k in keys]
    out = lines[:start] + [head, sep] + rows + lines[end:]

    print("解析到 %d 题 | 新增 %d | 更新 %d | 索引总行 %d" % (len(entries), added, updated, len(rows)))
    if dry:
        print("\n--- 预览（前 12 行）---")
        for r in rows[:12]:
            print(r)
        print("\n（--dry 模式，未写入）")
        return
    QA.write_text("\n".join(out), encoding="utf-8", newline="\n")
    print("已写入：%s" % QA)


if __name__ == "__main__":
    main()
