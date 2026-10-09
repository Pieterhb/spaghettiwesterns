import json
data = json.loads(open('westerns.json', encoding='utf-8').read())
check_ids = [1, 19, 105, 270, 515, 396, 2, 179]
for m in data:
    if m['id'] in check_ids:
        print(f"ID {m['id']:3}: {m['title'][:42]:42} year={m['year']}  slug={m['slug']}")

# Also check Frank Brana encoding
print()
for m in data:
    for cs in m.get('co_stars', []):
        if 'Bra' in cs and ('na' in cs or '\xf1' in cs):
            print(f"Frank check: {repr(cs)}")
            break
