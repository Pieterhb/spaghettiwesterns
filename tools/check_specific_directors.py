import csv

with open('Complete_Westerns.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

check_directors = [
    'Canavari',
    'Fizarotti',
    'Demichelli',
    'Squittieri',
    'Greepy',
    'Fulgozzi',
    'Croccolo',
    'Selander',
    'Nude Django',
    'Esteba',
    'Salvi',
    'Mattóli',
    'Bastia'
]

for idx, r in enumerate(rows):
    d = r['Director']
    t = r['Title']
    for cd in check_directors:
        if cd.lower() in d.lower() or cd.lower() in t.lower():
            print(f"[{idx+1}] {t} ({r['Year']})")
            print(f"    Director: {d}")
            print(f"    Lead:     {r['Lead_Actor']}")
            print(f"    Co-stars: {r['Co_Stars'][:80]}...")
            print()
            break
