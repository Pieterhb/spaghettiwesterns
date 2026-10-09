import csv, re

with open('Complete_Westerns.csv', encoding='utf-8', errors='replace') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Total rows in CSV: {len(rows)}")

# Check for specific suspicious characters: @, ?, strange accents, digits in names
suspicious = []

for idx, r in enumerate(rows):
    title = r['Title']
    for col, val in r.items():
        if not val:
            continue
        # Check for @
        if '@' in val:
            suspicious.append((idx+1, title, col, '@ character', val))
        # Check for replacement char
        if '\ufffd' in val:
            suspicious.append((idx+1, title, col, 'Replacement character U+FFFD', val))
        # Check for control chars
        if re.search(r'[\x00-\x1f\x7f]', val):
            suspicious.append((idx+1, title, col, 'Control character', repr(val)))
        # Check for odd character combos like JosAc, BraA, etc.
        if re.search(r'\b[A-Za-z]+A[c\xb1\xa0\x84\x9d]', val):
            suspicious.append((idx+1, title, col, 'Latin1-UTF8 garble', val))
        # Check for question marks in names (often OCR or conversion artifact for accented char)
        if col in ('Director', 'Lead_Actor', 'Co_Stars', 'Music') and '?' in val:
            suspicious.append((idx+1, title, col, 'Question mark in name', val))
        # Check for numbers in names (like 0 instead of O, 1 instead of l)
        if col in ('Director', 'Lead_Actor', 'Music') and re.search(r'[a-zA-Z]+[0-9]+[a-zA-Z]+', val):
            suspicious.append((idx+1, title, col, 'Number inside name', val))

print(f"Total suspicious findings: {len(suspicious)}")
for s in suspicious:
    print(f"Row {s[0]} [{s[1]}] - Col: {s[2]} ({s[3]}):")
    print(f"   {s[4]}")
