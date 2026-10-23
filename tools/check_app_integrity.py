import json, re

data = json.loads(open('westerns.json', encoding='utf-8').read())

year_changed_ids = [1,2,19,33,38,68,96,105,114,122,145,146,148,150,158,159,165,
                    179,184,205,248,249,258,261,263,267,270,283,315,324,355,379,
                    396,399,436,440,461,474,479,515,559]

print("=== 1. SLUG-YEAR CONSISTENCY (year-changed movies) ===")
mismatches = []
for m in data:
    if m['id'] in year_changed_ids:
        slug_year = re.search(r'-(\d{4})$', m['slug'])
        slug_yr = slug_year.group(1) if slug_year else 'NONE'
        status = 'OK' if slug_yr == m['year'] else 'MISMATCH'
        if status == 'MISMATCH':
            mismatches.append(m)
        print(f"  [{status}] ID {m['id']:3d} | year={m['year']} | slug={m['slug']}")

print()
if mismatches:
    print(f"FAILURES: {len(mismatches)} slug-year mismatches found!")
else:
    print("All slug-year pairs match. OK")

print()
print("=== 2. ALL SLUGS UNIQUE ===")
slugs = [m['slug'] for m in data]
dupes = [s for s in set(slugs) if slugs.count(s) > 1]
if dupes:
    print("DUPLICATE SLUGS FOUND:", dupes)
else:
    print(f"All {len(slugs)} slugs are unique. OK")

print()
print("=== 3. _worker.js LOOKUP CONTAINS NEW SLUGS ===")
worker = open('_worker.js', encoding='utf-8').read()
# Check a sample of the new slugs are in the worker
check_slugs = [
    'ace-high-1968',       # was ace-high-1967
    'keoma-1976',          # was keoma-1975
    'return-of-sabata-1971',  # was 1972
    'hellbenders-1967',    # was 1966
    'dynamite-jack-1961',  # was 1963
    'yankee-1966',         # was 1967
    'wanted-1966',         # was 1968
]
old_slugs = [
    'ace-high-1967',
    'keoma-1975',
    'return-of-sabata-1972',
    'hellbenders-1966',
    'dynamite-jack-1963',
    'yankee-1967',
    'wanted-1968',
]
for slug in check_slugs:
    found = slug in worker
    print(f"  [{'FOUND' if found else 'MISSING'}] New slug: {slug}")

print()
for slug in old_slugs:
    found = slug in worker
    print(f"  [{'PROBLEM-STILL-IN' if found else 'CLEAN'}] Old slug: {slug}")

print()
print("=== 4. archive.html CONTAINS NEW SLUGS ===")
archive = open('archive.html', encoding='utf-8').read()
for slug in check_slugs:
    found = slug in archive
    print(f"  [{'FOUND' if found else 'MISSING'}] New slug in archive: {slug}")
for slug in old_slugs:
    found = slug in archive
    print(f"  [{'PROBLEM-STILL-IN' if found else 'CLEAN'}] Old slug in archive: {slug}")

print()
print("=== 5. sitemap.xml CONTAINS NEW SLUGS ===")
sitemap = open('sitemap.xml', encoding='utf-8').read()
for slug in check_slugs:
    found = slug in sitemap
    print(f"  [{'FOUND' if found else 'MISSING'}] New slug in sitemap: {slug}")
for slug in old_slugs:
    found = slug in sitemap
    print(f"  [{'PROBLEM-STILL-IN' if found else 'CLEAN'}] Old slug in sitemap: {slug}")

print()
print("=== 6. index.html - hardcoded film slugs ===")
index = open('index.html', encoding='utf-8').read()
old_slug_hits = [s for s in old_slugs if s in index]
print("Old slugs hardcoded in index.html:", old_slug_hits if old_slug_hits else "None. OK")

print()
print("=== 7. app.js - how slugs are used ===")
appjs = open('app.js', encoding='utf-8').read()
# Check for hardcoded slugs - any film slug hardcoded would be a bug
old_slug_hits = [s for s in old_slugs if s in appjs]
print("Old slugs hardcoded in app.js:", old_slug_hits if old_slug_hits else "None. OK")
# Confirm slug-based lookup pattern
has_slug_lookup = 'm.slug === filmSlug' in appjs or "m.slug === slug" in appjs
print("Slug-based movie lookup pattern present:", has_slug_lookup)
has_slug_push = 'encodeURIComponent(movie.slug)' in appjs
print("URL slug encoding on pushState present:", has_slug_push)
has_popstate = 'popstate' in appjs
print("popstate (back/forward browser nav) handled:", has_popstate)
