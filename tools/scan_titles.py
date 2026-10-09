import csv, re

with open('Complete_Westerns.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

suspicious_titles = []
for idx, r in enumerate(rows):
    mid = idx + 1
    t = r['Title']
    alt = r['Alternative_Titles']
    # Check if Title has weird punctuation
    if re.search(r'[\@\#\$\%\^\&\*\_\[\]\{\}\<\>\\]', t):
        suspicious_titles.append((mid, t, 'Symbol in Title', t))
    if re.search(r'[\@\#\$\%\^\&\*\_\[\]\{\}\<\>\\]', alt):
        suspicious_titles.append((mid, t, 'Symbol in Alt Title', alt))
    if t.count('(') != t.count(')'):
        suspicious_titles.append((mid, t, 'Unmatched paren in Title', t))

print(f"Suspicious titles found: {len(suspicious_titles)}")
for st in suspicious_titles:
    print(f"[{st[0]}] {st[1]} -> {st[2]}: {st[3]}")
