"""
apply_full_name_and_ocr_fixes.py
Applies verified Director, Lead Actor, Co-Star, and Music fixes to Complete_Westerns.csv,
then rebuilds all derived data (westerns.json, archive.html, sitemap.xml, _worker.js),
and creates a full backup.
"""

import csv
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

CSV_FILE = Path("Complete_Westerns.csv")
JSON_FILE = Path("westerns.json")
BACKUP_DIR = Path("backups")
BACKUP_DIR.mkdir(exist_ok=True)

# 1. Take initial backup
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
pre_backup_dir = BACKUP_DIR / f"pre_names_fix_backup_{ts}"
pre_backup_dir.mkdir(exist_ok=True)
shutil.copy2(CSV_FILE, pre_backup_dir / CSV_FILE.name)
shutil.copy2(JSON_FILE, pre_backup_dir / JSON_FILE.name)
print(f"[OK] Pre-fix backup created in: {pre_backup_dir}")

# 2. Define targeted fixes by Movie ID
DIRECTOR_FIXES = {
    38:  ("Cesare Canavari", "Cesare Canevari"),
    60:  ("Ron Elliot", "Byron Mabe"),
    126: ("Tullio Demichelli", "Tullio Demicheli"),
    150: ("Carlo Croccolo (as Söbey Martin)", "Sobey Martin"),
    158: ("Augustin Navarro", "Agustín Navarro"),
    185: ("Tullio Demichelli", "Tullio Demicheli"),
    217: ("Gottfried Kölditz", "Gottfried Kolditz"),
    226: ("Manuel Esteba (as Ted Mulligan)", "Manuel Esteba / Antonio Mollica (as Ted Mulligan)"),
    232: ("Primo Zeglio (as Anthony Greepy)", "Primo Zeglio (as Anthony Green)"),
    245: ("Pasquale Squittieri (as William Redford)", "Pasquale Squitieri (as William Redford)"),
    249: ("Erminio Salvi", "Emimmo Salvi"),
    369: ("Niska Fulgozzi / Burt Kennedy", "Nikša Fulgosi / Burt Kennedy"),
    376: ("Pasquale Squittieri (as William Redford)", "Pasquale Squitieri (as William Redford)"),
    464: ("Tullio Demichelli", "Tullio Demicheli"),
    501: ("Ettore Fizarotti", "Ettore Maria Fizzarotti"),
    555: ("Tullio Demichelli", "Tullio Demicheli"),
}

LEAD_ACTOR_FIXES = {
    45:  ("Hardy Kruger", "Hardy Krüger"),
    83:  ("Harald Leignitz", "Harald Leipnitz"),
}

MUSIC_FIXES = {
    106: ("Maurio Ghiari", "Mauro Chiari"),
    547: ("Marcello Romoino", "Marcello Ramoino"),
}

COSTAR_EXACT_REPLACEMENTS = [
    # Fix comma-separated suffix split for Harry Carey Jr.
    ("Harry Carey, Jr.", "Harry Carey Jr."),
    # Actor typo fixes
    ("Simon Arraga", "Simón Arriaga"),
    ("Richard Melvill,", "Richard Melville,"),
    ("Rosella Bergamonti", "Rossella Bergamonti"),
    ("Hans Nielson", "Hans Nielsen"),
    ("Andres Mesuto", "Andrés Mejuto"),
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
    ("Mike Brendell", "Mike Brendel"),
]

# Read CSV rows
rows = []
with open(CSV_FILE, encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

dir_applied = 0
lead_applied = 0
music_applied = 0
costar_applied = 0

for idx, r in enumerate(rows):
    mid = idx + 1
    
    # 1. Director fix
    if mid in DIRECTOR_FIXES:
        old, new = DIRECTOR_FIXES[mid]
        if old in r["Director"]:
            r["Director"] = r["Director"].replace(old, new)
            dir_applied += 1
            print(f"  [Director] ID {mid} {r['Title']}: {old} -> {new}")
            
    # 2. Lead actor fix
    if mid in LEAD_ACTOR_FIXES:
        old, new = LEAD_ACTOR_FIXES[mid]
        if old in r["Lead_Actor"]:
            r["Lead_Actor"] = r["Lead_Actor"].replace(old, new)
            lead_applied += 1
            print(f"  [Lead Actor] ID {mid} {r['Title']}: {old} -> {new}")
            
    # 3. Music fix
    if mid in MUSIC_FIXES:
        old, new = MUSIC_FIXES[mid]
        if old in r["Music"]:
            r["Music"] = r["Music"].replace(old, new)
            music_applied += 1
            print(f"  [Music] ID {mid} {r['Title']}: {old} -> {new}")
            
    # 4. Co-star fixes
    for old_cs, new_cs in COSTAR_EXACT_REPLACEMENTS:
        if old_cs in r["Co_Stars"]:
            r["Co_Stars"] = r["Co_Stars"].replace(old_cs, new_cs)
            costar_applied += 1
            print(f"  [Co-Star] ID {mid} {r['Title']}: {old_cs} -> {new_cs}")

print(f"\nSummary of patches applied to CSV:")
print(f"  Directors patched:    {dir_applied}")
print(f"  Lead Actors patched:  {lead_applied}")
print(f"  Music patched:        {music_applied}")
print(f"  Co-Stars patched:     {costar_applied}")

# Save updated CSV
with open(CSV_FILE, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"[OK] Patched CSV saved: {CSV_FILE}")

# Rebuild all derived data
print("\nRebuilding application data with build_data.py...")
res = subprocess.run([sys.executable, "build_data.py"], capture_output=True, text=True)
print(res.stdout)
if res.returncode != 0:
    print("[ERROR] build_data.py failed:")
    print(res.stderr)
    sys.exit(1)

# Verify with spot checks on updated westerns.json
print("Verifying updated westerns.json spot checks...")
with open(JSON_FILE, encoding="utf-8") as f:
    data = json.load(f)

checks = [
    (38, "director", "Cesare Canevari"),
    (60, "director", "Byron Mabe"),
    (126, "director", "Tullio Demicheli"),
    (150, "director", "Sobey Martin"),
    (232, "director", "Primo Zeglio (as Anthony Green)"),
    (45, "lead_actor", "Hardy Krüger"),
    (83, "lead_actor", "Harald Leipnitz"),
    (106, "music", "Mauro Chiari"),
    (547, "music", "Marcello Ramoino"),
    (28, "co_stars", "Harry Carey Jr."),
    (53, "co_stars", "Simón Arriaga"),
    (319, "co_stars", "Glauco Onorato"),
    (479, "co_stars", "Norma Bengell"),
]

all_passed = True
for mid, field, expected in checks:
    m = next(x for x in data if x["id"] == mid)
    val = m[field]
    if isinstance(val, list):
        passed = expected in val
        actual = [v for v in val if expected in v or expected.split()[0] in v]
    else:
        passed = expected in val
        actual = val
    status = "PASS" if passed else "FAIL"
    if not passed:
        all_passed = False
    print(f"  [{status}] ID {mid} {field}: expected '{expected}', found: {actual}")

if not all_passed:
    print("[ERROR] Some spot checks failed!")
    sys.exit(1)

# Create full project backup
post_backup_dir = BACKUP_DIR / f"full_project_backup_{ts}_names_and_ocr_fixed"
post_backup_dir.mkdir(exist_ok=True)
backup_files = [
    "westerns.json",
    "Complete_Westerns.csv",
    "archive.html",
    "_worker.js",
    "sitemap.xml",
    "index.html",
    "style.css",
    "app.js",
    "about.html",
    "contact.html",
    "privacy.html",
    "terms.html"
]

for bf in backup_files:
    p = Path(bf)
    if p.exists():
        shutil.copy2(p, post_backup_dir / p.name)

print(f"\n[OK] Full project backup created: {post_backup_dir}")
print("ALL TASKS COMPLETED SUCCESSFULLY!")
