import csv, re

with open('Complete_Westerns.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

pseudonyms = []
for idx, r in enumerate(rows):
    line = f"{r['Director']} | {r['Lead_Actor']} | {r['Co_Stars']}"
    matches = re.findall(r'\(as [^\)]+\)', line)
    for m in matches:
        pseudonyms.append((idx+1, r['Title'], m))

print(f"Total pseudonyms found: {len(pseudonyms)}")
for p in pseudonyms:
    print(f"[{p[0]}] {p[1]}: {p[2]}")
