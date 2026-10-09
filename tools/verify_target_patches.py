import csv

with open('Complete_Westerns.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

# Define all verified corrections
DIRECTOR_PATCHES = {
    38:  ("Cesare Canavari", "Cesare Canevari"),
    60:  ("Ron Elliot", "Byron Mabe"),
    126: ("Tullio Demichelli", "Tullio Demicheli"),
    150: ("Carlo Croccolo (as Sbey Martin)", "Sobey Martin"),
    150: ("Carlo Croccolo (as Sobey Martin)", "Sobey Martin"),
    158: ("Augustin Navarro", "Agustn Navarro"),
    185: ("Tullio Demichelli", "Tullio Demicheli"),
    226: ("Manuel Esteba (as Ted Mulligan)", "Manuel Esteba / Antonio Mollica (as Ted Mulligan)"),
    232: ("Primo Zeglio (as Anthony Greepy)", "Primo Zeglio (as Anthony Green)"),
    245: ("Pasquale Squittieri (as William Redford)", "Pasquale Squitieri (as William Redford)"),
    249: ("Erminio Salvi", "Emimmo Salvi"),
    369: ("Niska Fulgozzi / Burt Kennedy", "Nika Fulgosi / Burt Kennedy"),
    376: ("Pasquale Squittieri (as William Redford)", "Pasquale Squitieri (as William Redford)"),
    464: ("Tullio Demichelli", "Tullio Demicheli"),
    501: ("Ettore Fizarotti", "Ettore Maria Fizzarotti"),
    555: ("Tullio Demichelli", "Tullio Demicheli"),
}

LEAD_PATCHES = {
    45:  ("Hardy Kruger", "Hardy Krger"),
    83:  ("Harald Leignitz", "Harald Leipnitz"),
}

MUSIC_PATCHES = {
    106: ("Maurio Ghiari", "Mauro Chiari"),
    547: ("Marcello Romoino", "Marcello Ramoino"),
}

# Substring replacements in Co_Stars
COSTAR_REPLACEMENTS = [
    ("Harry Carey, Jr.", "Harry Carey Jr."),
    ("Simon Arraga", "Simn Arriaga"),
    ("Richard Melvill,", "Richard Melville,"),
    ("Rosella Bergamonti", "Rossella Bergamonti"),
    ("Hans Nielson", "Hans Nielsen"),
    ("Andres Mesuto", "Andrs Mejuto"),
    ("Joe Karmel", "Joe Kamel"),
    ("Daniella Igliozzi", "Daniela Igliozzi"),
    ("Marisa Salinas", "Marisa Solinas"),
    ("Clauco Onorato", "Glauco Onorato"),
    ("Luigi Vanucchi", "Luigi Vannucchi"),
    ("Yvonne Bastion", "Yvonne Bastien"),
    ("Norma Benguel", "Norma Bengell"),
    ("Eleonara Bianchi", "Eleonora Bianchi"),
    ("Massimo Carocci", "Massimo Carrocci"),
    ("Rick Battaglia", "Rik Battaglia"),
]

print("Verifying target matches in rows...")
for idx, r in enumerate(rows):
    mid = idx + 1
    if mid in DIRECTOR_PATCHES:
        old, new = DIRECTOR_PATCHES[mid]
        print(f"Director [{mid}] {r['Title']}: current={r['Director']!r} -> {new!r}")
    if mid in LEAD_PATCHES:
        old, new = LEAD_PATCHES[mid]
        print(f"Lead [{mid}] {r['Title']}: current={r['Lead_Actor']!r} -> {new!r}")
    if mid in MUSIC_PATCHES:
        old, new = MUSIC_PATCHES[mid]
        print(f"Music [{mid}] {r['Title']}: current={r['Music']!r} -> {new!r}")
    for old_cs, new_cs in COSTAR_REPLACEMENTS:
        if old_cs in r['Co_Stars']:
            print(f"Co-Star [{mid}] {r['Title']}: matched {old_cs!r} -> {new_cs!r}")
