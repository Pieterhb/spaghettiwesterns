import json

report = json.loads(open('corrections_report.json', encoding='utf-8').read())
cache = json.loads(open('verify_cache.json', encoding='utf-8').read())

dir_issues = [r for r in report if r.get('field') == 'director']
print(f"Total director issues: {len(dir_issues)}")

for d in dir_issues:
    mid = str(d['movie_id'])
    entry = cache.get(mid, {})
    swdb = entry.get('swdb', {})
    people = swdb.get('people', []) if swdb else []
    print(f"\n--- [{d['movie_id']}] {d['movie_title']} ({d['movie_year']}) ---")
    print(f"  Our Director: {d['our_value']}")
    print(f"  SWDb Title:   {swdb.get('swdb_title', 'N/A')}")
    print(f"  SWDb People:  {people[:8]}")
