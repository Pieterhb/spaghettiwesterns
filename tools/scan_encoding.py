"""Scan westerns.json and Complete_Westerns.csv for encoding artifacts."""
import json, re, csv

# ── Scan westerns.json ────────────────────────────────────────────────────────
raw = open('westerns.json', encoding='utf-8').read()

non_ascii = sorted(set(c for c in raw if ord(c) > 127), key=ord)
print('Non-ASCII chars in westerns.json:')
for c in non_ascii:
    print(f'  U+{ord(c):04X}  {repr(c)}  -> {c}')

# Known garbled patterns from PDF extraction
garbled_pats = [
    r'JosA[ce\xc9\xe9]\b',
    r'BraA[n\xf1\xc3\xb1]',
    r'InduA[n\xf1]',
    r'GA\x14tz',
    r'Ac\b',        # José -> JosAc in latin1-to-utf8 double-encoding
    r'A\xef\xbf\xbd',  # replacement char after A
]

data = json.loads(raw)

def all_strings(movie):
    """Yield (field, string) for all string values in a movie record."""
    for field, val in movie.items():
        if isinstance(val, str):
            yield field, val
        elif isinstance(val, list):
            for item in val:
                if isinstance(item, str):
                    yield field, item

hits = []
for movie in data:
    for field, s in all_strings(movie):
        for pat in garbled_pats:
            if re.search(pat, s):
                hits.append((movie['id'], movie['title'], field, s))
                break

print(f'\nGarbled-pattern hits in westerns.json: {len(hits)}')
for h in hits[:30]:
    print(f'  [{h[0]}] {h[2]}: {repr(h[3][:80])}')

# ── Also scan the CSV source ──────────────────────────────────────────────────
print('\n--- CSV scan ---')
csv_hits = []
with open('Complete_Westerns.csv', encoding='utf-8', errors='replace') as f:
    reader = csv.DictReader(f)
    for row in reader:
        for field, val in row.items():
            if val and re.search(r'[A-Z][a-z]?A[c\xc3\xb1\xf1\xe9\xe1\x84]|A\xa0|JosAc|BraA|InduA|\x14|\ufffd', val):
                csv_hits.append((row.get('Title','?'), field, repr(val[:80])))

print(f'Garbled hits in CSV: {len(csv_hits)}')
for h in csv_hits[:40]:
    print(f'  [{h[1]}] {h[0]!r:.30}: {h[2]}')
