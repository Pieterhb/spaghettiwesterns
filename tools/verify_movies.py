"""
Spaghetti Western Fact-Checker
================================
Strategy (most reliable first, least credit-hungry first):

Phase 1 - SWDb MediaWiki API (FREE, no Firecrawl credits)
  - Hits spaghetti-western.net's public /api.php
  - Gets year, director, full cast from categories
  - Handles redirects (e.g. "Ace High" -> "Quattro dell'Ave Maria, I")

Phase 2 - Firecrawl /v1/search (uses credits, for unmatched / to add Wikipedia source)
  - Searches Wikipedia + IMDb for movies not found on SWDb
  - Also uses scraped description snippets for year cross-check

Phase 3 - Comparison & report
  - Compares app data field-by-field against gathered reference data
  - Outputs corrections_report.json + human-readable corrections_report.md
"""

import json
import time
import re
import requests
from pathlib import Path
from urllib.parse import quote

# ── Config ──────────────────────────────────────────────────────────────────
WESTERNS_JSON  = Path("westerns.json")
REPORT_JSON    = Path("corrections_report.json")
REPORT_MD      = Path("corrections_report.md")
CACHE_FILE     = Path("verify_cache.json")      # saves progress between runs
FIRECRAWL_KEY  = "fc-eb0c854fdd29460a8dbc13c70c4b9915"
SWDB_API       = "https://www.spaghetti-western.net/api.php"
FC_SEARCH_URL  = "https://api.firecrawl.dev/v1/search"
HEADERS_SWDB   = {"User-Agent": "SpaghettiWesternFactChecker/1.0"}
HEADERS_FC     = {"Authorization": f"Bearer {FIRECRAWL_KEY}", "Content-Type": "application/json"}
SWDB_DELAY     = 0.4   # seconds between SWDb API calls (be polite)
FC_DELAY       = 1.2   # seconds between Firecrawl calls

# ── Load data ────────────────────────────────────────────────────────────────
print("Loading westerns.json ...")
movies = json.loads(WESTERNS_JSON.read_text(encoding="utf-8"))
print(f"  {len(movies)} movies loaded.\n")

# Load or init cache
if CACHE_FILE.exists():
    cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    print(f"Resuming from cache ({len(cache)} movies already processed).\n")
else:
    cache = {}

def save_cache():
    CACHE_FILE.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")

# ── Phase 1: SWDb MediaWiki API ──────────────────────────────────────────────

def swdb_lookup(title: str) -> dict | None:
    """
    Query the SWDb MediaWiki API.
    Returns a dict with keys: swdb_title, year, director, cast, url
    Returns None if page not found.
    """
    try:
        resp = requests.get(SWDB_API, params={
            "action": "query",
            "titles": title,
            "prop": "categories|info",
            "cllimit": "500",
            "inprop": "url",
            "format": "json",
            "redirects": 1
        }, headers=HEADERS_SWDB, timeout=12)
        data = resp.json()
    except Exception as e:
        print(f"    SWDb API error for '{title}': {e}")
        return None

    pages = data.get("query", {}).get("pages", {})
    page = next(iter(pages.values()))
    if "missing" in page:
        return None

    categories = [c["title"].replace("Category:", "") for c in page.get("categories", [])]

    # Extract year (category like "1967")
    years = [c for c in categories if re.fullmatch(r"\d{4}", c)]

    # Extract director & cast (everything that isn't a metadata category)
    META_CATS = {
        "All", "Stubs", "Resources", "Features", "Circus Western",
        "Eurowestern", "Hill & Spencer", "Zapata Western",
    }
    # Director is typically listed first under crew categories; 
    # SWDb doesn't separate director from cast in categories, so we'll note all people
    people = [c for c in categories if c not in META_CATS
              and not re.fullmatch(r"\d{4}", c)
              and not c.startswith("Italy") and not c.startswith("Spain")
              and not c.startswith("West Germany") and not c.startswith("France")
              and not c.startswith("Yugoslavia")]

    return {
        "swdb_title": page.get("title", title),
        "year": years[0] if years else None,
        "people": people,      # includes director + cast (not separated at category level)
        "url": page.get("fullurl", f"https://www.spaghetti-western.net/index.php/{quote(title)}"),
        "source": "SWDb"
    }

def swdb_lookup_with_alts(movie: dict) -> dict | None:
    """Try main title, then alt_titles."""
    titles_to_try = [movie["title"]] + movie.get("alt_titles", [])
    for t in titles_to_try:
        result = swdb_lookup(t)
        time.sleep(SWDB_DELAY)
        if result:
            return result
    return None

# ── Phase 2: Firecrawl search (fallback) ─────────────────────────────────────

def firecrawl_search(title: str, year: str) -> dict | None:
    """
    Use Firecrawl search to find Wikipedia / IMDb info.
    Extracts director + cast from description snippets.
    """
    query = f'"{title}" {year} spaghetti western film director cast'
    try:
        resp = requests.post(FC_SEARCH_URL, headers=HEADERS_FC,
                             json={"query": query, "limit": 3}, timeout=30)
        data = resp.json()
    except Exception as e:
        print(f"    Firecrawl error for '{title}': {e}")
        return None

    if not data.get("success"):
        return None

    results = data.get("data", [])
    # Prefer Wikipedia or IMDb
    for r in results:
        url = r.get("url", "")
        desc = r.get("description", "")
        title_r = r.get("title", "")
        if "wikipedia.org" in url or "imdb.com" in url or "letterboxd.com" in url:
            return {
                "url": url,
                "title_found": title_r,
                "description": desc,
                "source": "Firecrawl/Search"
            }
    if results:
        r = results[0]
        return {
            "url": r.get("url"),
            "title_found": r.get("title"),
            "description": r.get("description"),
            "source": "Firecrawl/Search"
        }
    return None

# ── Phase 3: Comparison ───────────────────────────────────────────────────────

def normalize_name(name: str) -> str:
    """Lowercase, remove punctuation, collapse spaces."""
    return re.sub(r"[^a-z0-9 ]", "", name.lower()).strip()

def name_in_list(name: str, people_list: list[str]) -> bool:
    """Check if a person's name appears in a list (normalized)."""
    n = normalize_name(name)
    return any(n in normalize_name(p) or normalize_name(p) in n for p in people_list)

def extract_year_from_desc(desc: str) -> str | None:
    """Extract a 4-digit year from a description string."""
    m = re.search(r"\b(19[4-9]\d|20[0-2]\d)\b", desc)
    return m.group(1) if m else None

def compare_movie(movie: dict, swdb: dict | None, fc: dict | None) -> list[dict]:
    """
    Compare movie fields against reference data.
    Returns a list of discrepancy dicts.
    """
    issues = []

    def flag(field, our_val, ref_val, source, confidence="medium", note=""):
        issues.append({
            "field": field,
            "our_value": our_val,
            "reference_value": ref_val,
            "source": source,
            "confidence": confidence,
            "note": note
        })

    if swdb:
        # ── Year check ──
        if swdb["year"] and movie.get("year") and swdb["year"] != str(movie["year"]):
            flag("year", movie["year"], swdb["year"], swdb["url"], "high",
                 f"SWDb categorises this film under {swdb['year']}")

        # ── Director check ──
        # Director appears in the people categories. Check if our director name
        # (stripped of pseudonyms) appears in SWDb people list.
        our_director_raw = movie.get("director", "")
        # Strip parenthetical pseudonyms: "Gianfranco Parolini (as Frank Kramer)" -> "Gianfranco Parolini"
        our_director_clean = re.sub(r"\s*\(as .+?\)", "", our_director_raw).strip()
        pseudonym = re.search(r"\(as (.+?)\)", our_director_raw)
        pseudonym_str = pseudonym.group(1) if pseudonym else None

        real_in_swdb   = name_in_list(our_director_clean, swdb["people"])
        pseudo_in_swdb = pseudonym_str and name_in_list(pseudonym_str, swdb["people"])

        if not real_in_swdb and not pseudo_in_swdb and our_director_clean:
            # Director not found in SWDb people at all → possible name error
            flag("director", our_director_raw, f"Not found in SWDb people: {swdb['people'][:5]}",
                 swdb["url"], "low",
                 "Director name not found in SWDb categories. Could be a name spelling error.")

        # ── Lead actor check ──
        our_lead = movie.get("lead_actor", "")
        # Strip parentheticals
        our_lead_clean = re.sub(r"\s*\(.+?\)", "", our_lead).strip()
        if our_lead_clean and not name_in_list(our_lead_clean, swdb["people"]):
            flag("lead_actor", our_lead, f"Not found in SWDb people: {swdb['people'][:8]}",
                 swdb["url"], "low",
                 "Lead actor name not found in SWDb categories.")

        # ── Co-stars spot check (just flag if a co-star is entirely absent) ──
        co_stars = movie.get("co_stars", [])
        missing_co = []
        for cs in co_stars[:5]:  # check first 5
            cs_clean = re.sub(r"\s*\(.+?\)", "", cs).strip()
            if cs_clean and not name_in_list(cs_clean, swdb["people"]):
                missing_co.append(cs)
        if missing_co:
            flag("co_stars", missing_co, "Some co-stars not found in SWDb",
                 swdb["url"], "low",
                 "These co-stars were not found in SWDb categories (may just be uncatalogued).")

    # ── Firecrawl / description-based checks ──
    if fc and not swdb:
        desc = fc.get("description", "")
        fc_year = extract_year_from_desc(desc)
        if fc_year and movie.get("year") and fc_year != str(movie["year"]):
            flag("year", movie["year"], fc_year, fc["url"], "medium",
                 f"Year from web search description: '{desc[:120]}'")

    return issues

# ── Main loop ─────────────────────────────────────────────────────────────────

print("=" * 60)
print("PHASE 1 - SWDb MediaWiki API lookups (free, no credits)")
print("=" * 60)

swdb_found    = 0
swdb_missing  = []
fc_credits_used = 0

for i, movie in enumerate(movies):
    mid = str(movie["id"])
    if mid in cache:
        # already processed this run or previous run
        continue

    title = movie["title"]
    year  = movie.get("year", "")
    print(f"[{i+1:3}/{len(movies)}] {title} ({year}) ...", end=" ", flush=True)

    swdb_data = swdb_lookup_with_alts(movie)
    issues    = []

    if swdb_data:
        swdb_found += 1
        print(f"[OK] SWDb: {swdb_data['swdb_title']}")
        issues = compare_movie(movie, swdb_data, None)
    else:
        swdb_missing.append(movie)
        print("[--] Not on SWDb")

    cache[mid] = {
        "id": movie["id"],
        "title": title,
        "year": year,
        "swdb": swdb_data,
        "fc": None,
        "issues": issues
    }

    # Save cache every 20 movies
    if (i + 1) % 20 == 0:
        save_cache()

save_cache()

print(f"\n[OK] SWDb matched: {swdb_found}/{len(movies)}")
print(f"[--] Not on SWDb: {len(swdb_missing)}")

print("\n" + "=" * 60)
print("PHASE 2 - Firecrawl search for unmatched movies")
print("=" * 60)

for i, movie in enumerate(swdb_missing):
    mid = str(movie["id"])
    title = movie["title"]
    year  = movie.get("year", "")
    print(f"[FC {i+1}/{len(swdb_missing)}] {title} ({year}) ...", end=" ", flush=True)

    fc_data = firecrawl_search(title, year)
    fc_credits_used += 1
    time.sleep(FC_DELAY)

    issues = []
    if fc_data:
        print(f"[OK] {fc_data['url']}")
        issues = compare_movie(movie, None, fc_data)
    else:
        print("[--] No results")

    cache[mid]["fc"]     = fc_data
    cache[mid]["issues"] = issues

    if (i + 1) % 10 == 0:
        save_cache()

save_cache()
print(f"\nFirecrawl credits used: ~{fc_credits_used}")

# ── Build report ──────────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("PHASE 3 - Building corrections report")
print("=" * 60)

all_issues = []
for mid, entry in cache.items():
    for issue in entry.get("issues", []):
        all_issues.append({
            "movie_id":    entry["id"],
            "movie_title": entry["title"],
            "movie_year":  entry["year"],
            **issue
        })

# Write JSON report
REPORT_JSON.write_text(json.dumps(all_issues, indent=2, ensure_ascii=False), encoding="utf-8")

# ── Write markdown report ─────────────────────────────────────────────────────
HIGH   = [i for i in all_issues if i["confidence"] == "high"]
MEDIUM = [i for i in all_issues if i["confidence"] == "medium"]
LOW    = [i for i in all_issues if i["confidence"] == "low"]

md_lines = [
    "# Spaghetti Western Data Corrections Report",
    "",
    f"> Generated by fact-checking {len(movies)} movies against the Spaghetti Western Database (SWDb) and web sources.",
    "",
    f"**Total discrepancies found:** {len(all_issues)}  ",
    f"- [HIGH] High confidence: {len(HIGH)}  ",
    f"- [MED] Medium confidence: {len(MEDIUM)}  ",
    f"- [LOW] Low confidence: {len(LOW)}  ",
    "",
    "---",
    "",
    "## [HIGH] High Confidence Corrections",
    "> These are almost certainly errors in your data.",
    "",
]

def movie_link(issue):
    return f"**[{issue['movie_title']} ({issue['movie_year']})]({issue['source']})**"

def render_issues(issues):
    lines = []
    for iss in issues:
        lines += [
            f"### {movie_link(iss)}",
            f"- **Field:** `{iss['field']}`",
            f"- **Your data:** `{iss['our_value']}`",
            f"- **Reference says:** `{iss['reference_value']}`",
            f"- **Note:** {iss['note']}",
            "",
        ]
    return lines

md_lines += render_issues(HIGH)
md_lines += [
    "---",
    "",
    "## [MED] Medium Confidence Corrections",
    "> These are likely errors; verify before changing.",
    "",
]
md_lines += render_issues(MEDIUM)
md_lines += [
    "---",
    "",
    "## [LOW] Low Confidence / Needs Review",
    "> These may be name spelling differences, omissions, or valid data that SWDb doesn't list.",
    "",
]
md_lines += render_issues(LOW)

# Summary table of movies not found on SWDb
md_lines += [
    "---",
    "",
    "## Movies Not Found on SWDb",
    f"These {len(swdb_missing)} movies had no match on spaghetti-western.net.",
    "They may be listed under a different title, or genuinely absent.",
    "",
    "| # | Title | Year |",
    "|---|-------|------|",
]
for m in swdb_missing:
    md_lines.append(f"| {m['id']} | {m['title']} | {m.get('year','')} |")

REPORT_MD.write_text("\n".join(md_lines), encoding="utf-8")

print(f"\n✅ Done!")
print(f"   corrections_report.json  → {len(all_issues)} total issues")
print(f"   corrections_report.md    → human-readable report")
print(f"   verify_cache.json        → saved lookup data")
print(f"\n   [HIGH] HIGH:   {len(HIGH)} issues (year mismatches, strongly confirmed)")
print(f"   [MED] MEDIUM: {len(MEDIUM)} issues")
print(f"   [LOW] LOW:    {len(LOW)} issues (name spelling / coverage gaps)")
