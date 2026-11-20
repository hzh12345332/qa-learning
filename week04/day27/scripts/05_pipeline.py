import csv
import sys


def iter_rows(path):
    """逐行产出 dict(不把整个文件读进内存)"""
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            print("读了：", row["userId"])
            yield row
            

def only_expected(rows, expected):
    """过滤：只留下 expected 等于指定值的行"""
    for r in rows:
        if r["expected"] == expected:
            yield r


def pick(rows, key):
    """变形：只取某一列"""
    for r in rows:
        yield r[key]


def main():
    path = "week04/day23/data/users.csv"
    #pipeline = pick(only_expected(iter_rows(path), "200"), "userId")
    #print(type(pipeline))
    print("① 造管道之前")
    pipeline = pick(only_expected(iter_rows(path), "200"), "userId")
    print("② 管道造好了，类型是：", type(pipeline).__name__)
    print("③ 现在才 list()")
    print("结果：", list(pipeline))


if __name__ == "__main__":
    main()