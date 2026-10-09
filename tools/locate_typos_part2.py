import csv

with open('Complete_Westerns.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

check_names = [
    'Clauco Onorato',
    'Harald Leignitz',
    'Andres Mesuto',
    'Norma Benguel',
    'Marisa Salinas',
    'Yvonne Bastion',
    'Hans Nielson',
    'Simon Arraga',
    'Daniella Igliozzi',
    'Rosella Bergamonti',
    'Massimo Carocci',
    'Richard Melvill',
    'Luigi Vanucchi',
    'Eleonara Bianchi',
    'Joe Karmel',
    'Anthony Greepy',
    'Canavari',
    'Fizarotti',
    'Demichelli',
    'Squittieri'
]

for idx in range(350, len(rows)):
    r = rows[idx]
    mid = idx + 1
    t = r['Title']
    line = f"{r['Director']} | {r['Lead_Actor']} | {r['Co_Stars']}"
    for cn in check_names:
        if cn.lower() in line.lower():
            print(f"[{mid}] {t.encode('ascii','replace').decode('ascii')}")
            print(f"   Match: {cn}")
            print(f"   Director: {r['Director'].encode('ascii','replace').decode('ascii')}")
            print(f"   Lead:     {r['Lead_Actor'].encode('ascii','replace').decode('ascii')}")
            print(f"   Co-Stars: {r['Co_Stars'].encode('ascii','replace').decode('ascii')}")
            print()
