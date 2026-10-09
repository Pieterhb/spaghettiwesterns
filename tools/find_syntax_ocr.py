import csv, re

with open('Complete_Westerns.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

print(f"Checking {len(rows)} rows for formatting, punctuation, OCR, and syntax bugs...")

issues = []

for idx, r in enumerate(rows):
    mid = idx + 1
    title = r['Title']
    
    # 1. Check unmatched parentheses
    for col in ('Title', 'Alternative_Titles', 'Director', 'Lead_Actor', 'Co_Stars', 'Music', 'Synopsis_and_Notes'):
        val = r[col]
        if val.count('(') != val.count(')'):
            issues.append((mid, title, col, 'Unmatched parentheses', val))
        if val.count('[') != val.count(']'):
            issues.append((mid, title, col, 'Unmatched brackets', val))
        if val.count('"') % 2 != 0:
            issues.append((mid, title, col, 'Unmatched quotes', val))
            
    # 2. Check double punctuation or odd spacing
    for col in ('Director', 'Lead_Actor', 'Co_Stars', 'Music'):
        val = r[col]
        if '  ' in val:
            issues.append((mid, title, col, 'Double space', val))
        if ',,' in val or ';;' in val:
            issues.append((mid, title, col, 'Double punctuation', val))
        if val.strip() != val:
            issues.append((mid, title, col, 'Leading/trailing whitespace', val))
        if val.endswith(',') or val.endswith(';'):
            issues.append((mid, title, col, 'Trailing comma/semicolon', val))

    # 3. Check for OCR artifacts like numbers inside words
    for col in ('Director', 'Lead_Actor', 'Music'):
        val = r[col]
        if re.search(r'[a-zA-Z]+[0-9]+', val):
            issues.append((mid, title, col, 'Number inside name (OCR)', val))

    # 4. Check for known misspellings of famous Western filmmakers/actors
    # Tullio Demichelli -> Tullio Demicheli
    if 'Demichelli' in r['Director']:
        issues.append((mid, title, 'Director', 'Misspelling: Demichelli (should be Demicheli)', r['Director']))
    # Demofilo Fidani
    if 'Fidani' in r['Director'] and 'Demofilo' not in r['Director'] and 'Miles Deem' not in r['Director']:
        issues.append((mid, title, 'Director', 'Check Fidani spelling', r['Director']))

print(f"Total issues found: {len(issues)}")
for iss in issues:
    print(f"[{iss[0]}] {iss[1]} | {iss[2]} -> {iss[3]}:")
    print(f"     {iss[4]}")
