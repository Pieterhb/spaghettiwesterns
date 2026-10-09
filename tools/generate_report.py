"""
Report generator - reads verify_cache.json and produces the corrections reports.
Run this after verify_movies.py has completed.
"""
import json, re
from pathlib import Path

CACHE_FILE  = Path("verify_cache.json")
REPORT_JSON = Path("corrections_report.json")
REPORT_MD   = Path("corrections_report.md")

cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
print(f"Loaded cache: {len(cache)} movies")

# ── Collect all issues ────────────────────────────────────────────────────────
all_issues = []
for mid, entry in cache.items():
    for issue in entry.get("issues", []):
        all_issues.append({
            "movie_id":    entry["id"],
            "movie_title": entry["title"],
            "movie_year":  entry["year"],
            **issue
        })

REPORT_JSON.write_text(json.dumps(all_issues, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Written: {REPORT_JSON} ({len(all_issues)} issues)")

HIGH   = [i for i in all_issues if i["confidence"] == "high"]
MEDIUM = [i for i in all_issues if i["confidence"] == "medium"]
LOW    = [i for i in all_issues if i["confidence"] == "low"]

# Movies not on SWDb
not_on_swdb = [(v["id"], v["title"], v["year"]) for v in cache.values() if not v.get("swdb")]
swdb_ok     = len(cache) - len(not_on_swdb)

# ── Year issues detail (HIGH) - extract the actual year discrepancies ─────────
year_issues = [i for i in HIGH if i["field"] == "year"]

# ── Build markdown ────────────────────────────────────────────────────────────
def movie_link(issue):
    src = issue.get("source", "#")
    return f"**[{issue['movie_title']} ({issue['movie_year']})]({src})**"

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

md = []
md += [
    "# Spaghetti Western Data Corrections Report",
    "",
    f"> Fact-checked {len(cache)} movies against the **Spaghetti Western Database (SWDb)** and web sources (Wikipedia, IMDb, Letterboxd).",
    f"> SWDb matched: **{swdb_ok}** movies. Firecrawl web-search used for the remaining **{len(not_on_swdb)}**.",
    "",
    f"**Total discrepancies found: {len(all_issues)}**",
    "",
    "| Confidence | Count | Meaning |",
    "|------------|-------|---------|",
    f"| HIGH | {len(HIGH)} | Almost certainly wrong — SWDb year/cast directly contradicts your data |",
    f"| MEDIUM | {len(MEDIUM)} | Likely wrong — web search description contradicts your data |",
    f"| LOW | {len(LOW)} | Needs review — name not found in reference (may be spelling/pseudonym) |",
    "",
    "---",
    "",
    "## HIGH Confidence Corrections",
    "> These are strongly confirmed by the Spaghetti Western Database.",
    "> **Recommended: fix these.**",
    "",
]
md += render_issues(HIGH)

md += [
    "---",
    "",
    "## MEDIUM Confidence Corrections",
    "> These come from web search result snippets (Wikipedia / IMDb descriptions).",
    "> Verify before applying.",
    "",
]
md += render_issues(MEDIUM)

md += [
    "---",
    "",
    "## LOW Confidence / Needs Review",
    "> Names not found in SWDb categories. Could be:",
    "> - Spelling differences between your book source and SWDb",
    "> - Pseudonyms not catalogued",  
    "> - Genuine errors",
    "> Review against the linked SWDb page before deciding.",
    "",
]
md += render_issues(LOW)

# Not-found table
md += [
    "---",
    "",
    "## Movies with NO Match on SWDb",
    f"These **{len(not_on_swdb)}** movies had no page on spaghetti-western.net (even after trying alternate titles).",
    "They may be listed under a different title, or are genuinely absent from SWDb.",
    "Firecrawl was used as a fallback for these.",
    "",
    "| ID | Title | Year |",
    "|----|-------|------|",
]
for mid, title, year in sorted(not_on_swdb):
    md.append(f"| {mid} | {title} | {year} |")

REPORT_MD.write_text("\n".join(md), encoding="utf-8")
print(f"Written: {REPORT_MD}")

# ── Console summary ────────────────────────────────────────────────────────────
print()
print("=" * 60)
print("CORRECTIONS SUMMARY")
print("=" * 60)
print(f"Total movies checked:  {len(cache)}")
print(f"Matched on SWDb:       {swdb_ok}")
print(f"Fallback (Firecrawl):  {len(not_on_swdb)}")
print()
print(f"Total issues:  {len(all_issues)}")
print(f"  HIGH:   {len(HIGH)}   <- fix these")
print(f"  MEDIUM: {len(MEDIUM)}   <- review these")
print(f"  LOW:    {len(LOW)}  <- spot-check these")
print()
print("HIGH confidence issues (year mismatches & confirmed errors):")
print("-" * 60)
for iss in HIGH:
    print(f"  [{iss['movie_title']} {iss['movie_year']}]")
    print(f"    Field:    {iss['field']}")
    print(f"    Yours:    {iss['our_value']}")
    print(f"    Correct:  {iss['reference_value']}")
    print()
