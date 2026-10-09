import csv, collections

with open('Complete_Westerns.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

directors = collections.Counter(r['Director'] for r in rows)
print(f"Total unique directors: {len(directors)}")

leads = collections.Counter(r['Lead_Actor'] for r in rows)
print(f"Total unique lead actors: {len(leads)}")

print("\n--- Directors list (sorted alphabetically) ---")
for d, cnt in sorted(directors.items(), key=lambda x: x[0].lower()):
    print(f"  {cnt:2d}x: {d}")
