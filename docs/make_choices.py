import csv
import json

fh = open("pairs.csv", "r", encoding="utf-8-sig")
reader = csv.DictReader(fh)
result = []
for i in range(1, 9):
    c1 = next(reader)
    c2 = next(reader)
    del (c1["Set"], c1["Type"])
    del (c2["Set"], c2["Type"])
    choice = {f"Choice{i}": {f"{i}A": c1, f"{i}B": c2}}
    result.append(choice)
fh.close()

with open("choices.json", "w", encoding="utf-8") as fo:
    json.dump(result, fo, indent=4, ensure_ascii=False)

print(json.dumps(result, indent=4, ensure_ascii=False))
