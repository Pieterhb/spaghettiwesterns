import csv, collections

with open('Complete_Westerns.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

leads = collections.Counter(r['Lead_Actor'] for r in rows)
print(f"Total unique lead actors: {len(leads)}")

for a, cnt in sorted(leads.items(), key=lambda x: x[0].lower()):
    print(f"  {cnt:2d}x: {a}")
