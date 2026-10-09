import csv, re

with open('Complete_Westerns.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

corruptions = []
for idx, r in enumerate(rows):
    mid = idx + 1
    t = r['Title']
    s = r['Synopsis_and_Notes']
    
    # words containing symbols like @, #, $, %, etc.
    bad_words = re.findall(r'\b\w*[@#\$%\*\^\{\}\[\]\|\\<>\ufffd]\w*\b', s)
    if bad_words:
        corruptions.append((mid, t, 'Symbol in word', bad_words))
        
    # double spaces
    if '  ' in s:
        pass # minor
        
print(f"Synopsis corruptions found: {len(corruptions)}")
for c in corruptions:
    print(f"[{c[0]}] {c[1]}: {c[3]}")
