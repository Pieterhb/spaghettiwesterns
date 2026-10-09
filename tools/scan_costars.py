import csv, collections, re

with open('Complete_Westerns.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

all_costars = []
for r in rows:
    cs_list = [c.strip() for c in r['Co_Stars'].split(',') if c.strip()]
    all_costars.extend(cs_list)

counter = collections.Counter(all_costars)
print(f"Total co-star credits: {len(all_costars)}")
print(f"Unique co-star names: {len(counter)}")

# Find suspicious names:
# 1. Names with odd characters or numbers
# 2. Names with known OCR patterns (like 'rn' -> 'm', 'cl' -> 'd', etc.)
# 3. Single-letter names or very short names
# 4. Incomplete parentheticals

suspicious_costars = []
for name, cnt in counter.items():
    if re.search(r'[\d@#\$%\*\^\{\}\[\]\|\\<>]', name):
        suspicious_costars.append((name, cnt, 'Unusual characters'))
    elif len(name) < 4:
        suspicious_costars.append((name, cnt, 'Very short name'))
    elif name.count('(') != name.count(')'):
        suspicious_costars.append((name, cnt, 'Unmatched parentheses'))
    elif name.startswith('as ') or name.startswith('and '):
        suspicious_costars.append((name, cnt, 'Broken prefix'))
    elif re.search(r'\b[a-z]', name) and not any(name.startswith(p) for p in ('de ', 'da ', 'del ', 'van ', 'von ', 'di ', 'la ', 'le ')):
        # lowercase start that isn't a known prefix
        pass

print(f"\nSuspicious co-star names: {len(suspicious_costars)}")
for sc in suspicious_costars:
    print(f"  {sc[1]}x: '{sc[0]}' ({sc[2]})")
