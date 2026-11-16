with open("week04/day23/data/demo.txt", "w", encoding="utf-8", newline="\n") as f:
    f.write("第一行：测试\n")
    f.write("第二行：接口\n")

with open("week04/day23/data/demo.txt", encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        print(i, line.rstrip())