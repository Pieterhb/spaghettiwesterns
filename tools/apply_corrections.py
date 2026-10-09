"""
Clean apply script - applies only verified corrections.
Restores from backup first, then applies only trusted fixes.
"""
import json, re, shutil
from pathlib import Path
from datetime import datetime

WESTERNS   = Path("westerns.json")
BACKUP_DIR = Path("backups")

# ── Step 0: Restore from pre-correction backup ────────────────────────────────
latest_backup = sorted(BACKUP_DIR.glob("westerns_backup_*.json"))[-1]
print(f"Restoring from backup: {latest_backup}")
shutil.copy2(latest_backup, WESTERNS)

# ── Load data ─────────────────────────────────────────────────────────────────
data = json.loads(WESTERNS.read_text(encoding="utf-8"))
print(f"Loaded {len(data)} movies.\n")

# ── VERIFIED year corrections ─────────────────────────────────────────────────
# HIGH confidence = from SWDb directly (authoritative)
# MEDIUM = only kept where the source description unambiguously states the year
# REJECTED = where year was from a review date, list page, or unrelated content

VERIFIED_YEAR_FIXES = {
    # id : (old_year, correct_year, reason)
    # ── HIGH confidence (SWDb) ────────────────────────────────────────────
    1:   ("1967", "1968", "SWDb: Ace High"),
    19:  ("1965", "1966", "SWDb: Arizona Colt"),
    33:  ("1963", "1964", "SWDb: Massacre at Fort Grant"),
    96:  ("1968", "1967", "SWDb: Red Blood, Yellow Gold"),
    105: ("1972", "1971", "SWDb: Return of Sabata"),
    114: ("1966", "1965", "SWDb: Ringo and His Golden Pistol"),
    122: ("1967", "1968", "SWDb: Run Man Run"),
    145: ("1968", "1969", "SWDb: Shadow of Sartana"),
    146: ("1963", "1962", "SWDb: Shadow of Zorro"),
    148: ("1969", "1970", "SWDb: Shango"),
    150: ("1965", "1964", "SWDb: Sheriff Was a Lady"),
    158: ("1965", "1964", "SWDb: Shots Ring Out!"),
    159: ("1972", "1971", "SWDb: Showdown for a Badman"),
    165: ("1966", "1965", "SWDb: Son of a Gunfighter"),
    184: ("1966", "1967", "SWDb: Ten Thousand Dollars Blood Money"),
    248: ("1968", "1966", "SWDb: Wanted"),
    249: ("1971", "1967", "SWDb: Wanted Johnny Texas"),
    258: ("1968", "1967", "SWDb: Winchester Does Not Forgive"),
    261: ("1967", "1966", "SWDb: Winnetou Thunder at the Border"),
    263: ("1963", "1964", "SWDb: Winnetou the Warrior"),
    267: ("1967", "1966", "SWDb: Yankee"),
    270: ("1974", "1975", "SWDb: Zorro"),
    283: ("1970", "1972", "SWDb: Ben and Charlie"),
    315: ("1976", "1977", "SWDb: California"),
    324: ("1972", "1973", "SWDb: Charley One-Eye"),
    379: ("1968", "1967", "SWDb: Django Kills Softly"),
    396: ("1963", "1961", "SWDb: Dynamite Jack"),
    399: ("1980", "1979", "SWDb: Eagles Wing"),
    436: ("1967", "1968", "SWDb: Garter Colt"),
    440: ("1968", "1967", "SWDb: Get the Coffin Ready"),
    461: ("1965", "1964", "SWDb: Gunfighters of Casa Grande"),
    479: ("1966", "1967", "SWDb: Hellbenders"),
    515: ("1975", "1976", "SWDb: Keoma"),
    559: ("1964", "1965", "SWDb: Man Called Gringo"),
    # ── MEDIUM confidence - accepted (clear year in title/description) ────
    2:   ("1969", "1970", "Web: Adios Cjamango 1970 - url slug confirms"),
    38:  ("1971", "1970", "Web: Matalo! 1970 Wikipedia spaghetti western list"),
    68:  ("1966", "1965", "SWDb: Outlaw of Red River"),
    179: ("1974", "1975", "Web: Take a Hard Ride - Wikipedia states 1975"),
    205: ("1972", "1973", "Web: Three Musketeers of West - IMDb credits page says 1973"),
    355: ("1970", "1971", "Web: Dead Men Ride - Wikipedia says 1971"),
    474: ("1967", "1969", "Web: Hatred of God - described as 1969 Italian-West German"),
    # ── MEDIUM confidence - REJECTED (bad source / review date / unrelated) ─
    # 92  Rampage at Apache Wells -> 2019  (2019 is a review date, not film year)
    # 118 Rita of the West -> 2015        (2015 is a Cinema Snob episode date)
    # 231 Two Gangsters in the Wild West->1995 (Letterboxd showing wrong film)
    # 234 Two R-R-Ringos from Texas->1970 (Germany release date vs Italy 1967)
    # 524 Killer Goodbye->1972            (description is about a different person)
    # 554 Man His Pride->2021             (2021 is a review date on the blog)
}

applied = 0
for mid, (old_yr, new_yr, reason) in VERIFIED_YEAR_FIXES.items():
    movie = next((m for m in data if m["id"] == mid), None)
    if not movie:
        print(f"  [WARN] ID {mid} not found")
        continue
    if movie["year"] != old_yr:
        print(f"  [SKIP] ID {mid} {movie['title']}: year is already {movie['year']} (expected {old_yr})")
        continue
    old_slug = movie.get("slug", "")
    new_slug = old_slug.replace(f"-{old_yr}", f"-{new_yr}")
    movie["year"] = new_yr
    movie["slug"] = new_slug
    print(f"  YEAR [{mid}] {movie['title']}: {old_yr} -> {new_yr}  ({reason})")
    applied += 1

print(f"\nYear corrections applied: {applied}\n")

# ── Encoding fixes ────────────────────────────────────────────────────────────
raw = json.dumps(data, ensure_ascii=False, indent=2)

EXACT_FIXES = [
    # Known PDF garbling - specific names first
    ("JosAc Maria Zabalza",    "José María Zabalza"),
    ("JosAc Luis Merino",      "José Luis Merino"),
    ("JosAc Antonio Balanos",  "José Antonio Balanos"),
    ("JosAc Truchado",         "José Truchado"),
    ("JosAc Maria Forque",     "José María Forqué"),
    ("Frank BraA\u00f1a",      "Frank Braña"),
    ("Frank Bra\u00f1a",       "Frank Braña"),  # if partially fixed already
    ("Luis InduA\u00f1i",      "Luis Induní"),
    ("GA\u0014tz George",      "Götz George"),
    # Generic encoding double-encodes
    ("\u00c3\u00a9",           "é"),
    ("\u00c3\u00b3",           "ó"),
    ("\u00c3\u00ba",           "ú"),
    ("\u00c3\u00a1",           "á"),
    ("\u00c3\u00ad",           "í"),
    ("\u00c3\u00b1",           "ñ"),
    ("\u00c3\u00b6",           "ö"),
    ("\u00c3\u00bc",           "ü"),
    ("\u00c3\u00a4",           "ä"),
    ("\u00c3\u00a8",           "è"),
    ("\u00c3\u00ac",           "ì"),
    ("\u00c3\u00b2",           "ò"),
    ("\u00c3\u00bb",           "û"),
    ("\u00c3\u00b9",           "ù"),
    # Inverted exclamation used as replacement char
    ("\u00a1",                 ""),
    # Catch-all JosAc (jose garbling)
    ("JosAc",                  "José"),
    # Ctrl char Götz
    ("GA\u0014",               "Gö"),
]

enc_applied = 0
for wrong, right in EXACT_FIXES:
    if wrong in raw:
        n = raw.count(wrong)
        raw = raw.replace(wrong, right)
        print(f"  ENC ({n}x): {repr(wrong)} -> {repr(right)}")
        enc_applied += n

# Regex catches for remaining patterns
def regex_fix(pattern, replacement, description):
    global raw, enc_applied
    fixed, n = re.subn(pattern, replacement, raw)
    if n:
        print(f"  ENC REGEX ({n}x): {description}")
        enc_applied += n
        raw = fixed

regex_fix(r'JosA[cC]\b',    'José',   'JosAc -> José')
regex_fix(r'BraA.a\b',      'Braña',  'BraAxa -> Braña')
regex_fix(r'InduA.i\b',     'Induní', 'InduAxi -> Induní')
regex_fix(r'GA\x14tz\b',    'Götz',   'GA+ctrl+tz -> Götz')

print(f"\nEncoding fixes applied: {enc_applied}\n")

# ── Validate & save ───────────────────────────────────────────────────────────
try:
    cleaned = json.loads(raw)
except json.JSONDecodeError as e:
    print(f"ERROR: JSON invalid: {e}")
    raise SystemExit(1)

# Take fresh backup of pre-clean original, then save
timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
final_backup = BACKUP_DIR / f"westerns_backup_{timestamp}.json"
shutil.copy2(latest_backup, final_backup)
print(f"Backup saved: {final_backup}")

WESTERNS.write_text(json.dumps(cleaned, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Saved: {WESTERNS}")

# ── Post-fix verification scan ────────────────────────────────────────────────
print("\n--- Post-fix verification ---")
final_raw = WESTERNS.read_text(encoding="utf-8")
check_patterns = [
    (r'JosA[cC]',  'JosAc (José garbling)'),
    (r'BraA[^n]',  'BraAx (Braña garbling)'),
    (r'InduA[^n]', 'InduAx (Induní garbling)'),
    (r'GA\x14',    'GA+ctrl (Götz garbling)'),
    (r'\u00a1',    'inverted exclamation'),
    (r'\ufffd',    'replacement char'),
]
clean = True
for pat, desc in check_patterns:
    hits = re.findall(pat, final_raw)
    if hits:
        print(f"  REMAINING: {desc} -> {hits[:3]}")
        clean = False
if clean:
    print("  All clean - no known encoding artifacts.")

print(f"""
==============================================
DONE
==============================================
  Backup:           {final_backup}
  Year fixes:       {applied}
  Encoding fixes:   {enc_applied}
  Total movies:     {len(cleaned)}
==============================================
""")
