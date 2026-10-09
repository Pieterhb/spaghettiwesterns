"""
Patches Complete_Westerns.csv with the verified year corrections,
then re-runs build_data.py to regenerate all derived files cleanly.
"""
import csv, shutil, subprocess, sys
from pathlib import Path
from datetime import datetime

CSV_FILE   = Path("Complete_Westerns.csv")
BACKUP_DIR = Path("backups")
BACKUP_DIR.mkdir(exist_ok=True)

# Backup the CSV
timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_backup = BACKUP_DIR / f"Complete_Westerns_backup_{timestamp}.csv"
shutil.copy2(CSV_FILE, csv_backup)
print(f"CSV backup: {csv_backup}")

# ── Verified year corrections: title (as in CSV) -> correct year ──────────────
# Key = exact Title field in CSV, Value = correct year string
YEAR_FIXES = {
    "Ace High":                                  "1968",
    "Adios Cjamango":                            "1970",
    "Arizona Colt":                              "1966",
    "Massacre at Fort Grant":                    "1964",
    "Matalo!":                                   "1970",
    "Outlaw of Red River":                       "1965",
    "Red Blood, Yellow Gold":                    "1967",
    "Return of Sabata":                          "1971",
    "Ringo and His Golden Pistol":               "1965",
    "Run Man, Run":                              "1968",
    "Shadow of Sartana... Shadow of Your Death": "1969",
    "Shadow of Zorro":                           "1962",
    "Shango":                                    "1970",
    "Sheriff Was a Lady":                        "1964",
    "Shots Ring Out!":                           "1964",
    "Showdown for a Badman":                     "1971",
    "Son of a Gunfighter":                       "1965",
    "Take a Hard Ride":                          "1975",
    "Ten Thousand Dollars Blood Money":          "1967",
    "Three Musketeers of the West":              "1973",
    "Wanted":                                    "1966",
    "Wanted Johnny Texas":                       "1967",
    "Winchester Does Not Forgive":               "1967",
    "Winnetou: Thunder at the Border":           "1966",
    "Winnetou the Warrior":                      "1964",
    "Yankee":                                    "1966",
    "Zorro":                                     "1975",
    "Ben and Charlie":                           "1972",
    "California":                                "1977",
    "Charley One-Eye":                           "1973",
    "Dead Men Ride":                             "1971",
    "Django Kills Softly":                       "1967",
    "Dynamite Jack":                             "1961",
    "Eagle's Wing":                              "1979",
    "Garter Colt":                               "1968",
    "Get the Coffin Ready":                      "1967",
    "Gunfighters of Casa Grande":                "1964",
    "Hatred of God":                             "1969",
    "Hellbenders":                               "1967",
    "Keoma":                                     "1976",
    "Man Called Gringo":                         "1965",
}

# ── Encoding fixes for CSV (same garbled patterns from PDF) ───────────────────
ENCODING_FIXES = [
    ("JosAc Maria Zabalza",   "José María Zabalza"),
    ("JosAc Luis Merino",     "José Luis Merino"),
    ("JosAc Antonio Balanos", "José Antonio Balanos"),
    ("JosAc Truchado",        "José Truchado"),
    ("JosAc Maria Forque",    "José María Forqué"),
    ("JosAc",                 "José"),
    ("BraA\xf1a",             "Braña"),
    ("BraA\ufffd",            "Braña"),
    ("InduA\xf1i",            "Induní"),
    ("InduA\ufffd",           "Induní"),
    ("GA\x14tz",              "Götz"),
    ("GA\x14",                "Gö"),
    ("\u00a1",                ""),
    ("\u00c3\u00a9",          "é"),
    ("\u00c3\u00b3",          "ó"),
    ("\u00c3\u00ba",          "ú"),
    ("\u00c3\u00a1",          "á"),
    ("\u00c3\u00ad",          "í"),
    ("\u00c3\u00b1",          "ñ"),
    ("\u00c3\u00b6",          "ö"),
    ("\u00c3\u00bc",          "ü"),
    ("\u00c3\u00a4",          "ä"),
    ("\u00c3\u00a8",          "è"),
    ("\u00c3\u00ac",          "ì"),
]

def fix_string(s):
    for wrong, right in ENCODING_FIXES:
        s = s.replace(wrong, right)
    return s

# ── Read, patch, write CSV ────────────────────────────────────────────────────
rows = []
year_applied = 0
enc_applied  = 0

with open(CSV_FILE, encoding="utf-8", errors="replace", newline="") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        title = row.get("Title", "")

        # Fix year
        if title in YEAR_FIXES:
            old_yr = row["Year"]
            row["Year"] = YEAR_FIXES[title]
            print(f"  YEAR: {title!r:50} {old_yr} -> {row['Year']}")
            year_applied += 1

        # Fix encoding in all fields
        for field in row:
            original = row[field]
            fixed    = fix_string(original)
            if fixed != original:
                enc_applied += 1
            row[field] = fixed

        rows.append(row)

print(f"\nYear fixes in CSV:     {year_applied}")
print(f"Encoding fixes in CSV: {enc_applied}")

with open(CSV_FILE, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"CSV saved: {CSV_FILE}")

# ── Rebuild all derived files from the patched CSV ───────────────────────────
print("\nRunning build_data.py ...")
result = subprocess.run([sys.executable, "build_data.py"], capture_output=True, text=True)
print(result.stdout)
if result.returncode != 0:
    print("ERROR:", result.stderr)
else:
    print("Build successful.")

# ── Final spot check ─────────────────────────────────────────────────────────
import json
data = json.loads(Path("westerns.json").read_text(encoding="utf-8"))
print("\n--- Spot check of fixed movies ---")
check = {1:"1968", 19:"1966", 105:"1971", 270:"1975", 515:"1976", 396:"1961"}
all_ok = True
for mid, expected_yr in check.items():
    m = next((x for x in data if x["id"] == mid), None)
    status = "OK" if m and m["year"] == expected_yr else "FAIL"
    if status == "FAIL":
        all_ok = False
    print(f"  [{status}] ID {mid}: {m['title'] if m else '?'} -> year={m['year'] if m else '?'} (expected {expected_yr})")

# Check Frank Brana encoding in final JSON
brana_samples = [cs for m in data for cs in m.get("co_stars", []) if "Bra" in cs and "\xf1" in cs]
print(f"\n  Frank Brania encoded correctly: {len(brana_samples)} occurrences found" if brana_samples else "\n  WARNING: Frank Brana encoding not found!")

print(f"""
==============================================
COMPLETE
==============================================
  CSV backup:        {csv_backup}
  Year fixes:        {year_applied}
  Encoding fixes:    {enc_applied}
  All spot checks:   {'PASSED' if all_ok else 'SOME FAILED - review above'}
==============================================
""")
