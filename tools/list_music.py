import csv, collections

with open('Complete_Westerns.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

musicians = collections.Counter(r['Music'] for r in rows)
print(f"Total unique music credits: {len(musicians)}")

for m, cnt in sorted(musicians.items(), key=lambda x: x[0].lower()):
    print(f"  {cnt:2d}x: {m}")
