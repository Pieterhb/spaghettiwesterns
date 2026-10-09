import json, requests, re

report = json.loads(open('corrections_report.json', encoding='utf-8').read())
cache = json.loads(open('verify_cache.json', encoding='utf-8').read())

lead_issues = [r for r in report if r.get('field') == 'lead_actor']
print(f"Checking {len(lead_issues)} lead actor issues against actual SWDb wikitext...")

headers = {'User-Agent': 'SpaghettiWesternFactChecker/1.0'}

for l in lead_issues:
    mid = str(l['movie_id'])
    entry = cache.get(mid, {})
    swdb_entry = entry.get('swdb')
    if not swdb_entry:
        continue
    swdb_title = swdb_entry['swdb_title']
    
    resp = requests.get('https://www.spaghetti-western.net/api.php', params={
        'action': 'query',
        'titles': swdb_title,
        'prop': 'revisions',
        'rvprop': 'content',
        'rvslots': 'main',
        'format': 'json',
        'redirects': 1
    }, headers=headers, timeout=12)
    
    data = resp.json()
    pages = data.get('query', {}).get('pages', {})
    page = next(iter(pages.values()), {})
    content = page.get('revisions', [{}])[0].get('slots', {}).get('main', {}).get('*', '')
    
    # Extract Cast line
    m = re.search(r"\*'''Cast'''[^\:]*:\s*([^\n]+)", content, re.IGNORECASE)
    cast_line = m.group(1).strip() if m else "NOT FOUND IN WIKITEXT"
    
    # Clean brackets/categories
    cast_clean = re.sub(r'\[\[Category:[^\|\]]+\|([^\]]+)\]\]', r'\1', cast_line)
    cast_clean = re.sub(r'\[\[([^\|\]]+)\]\]', r'\1', cast_clean)
    cast_clean = re.sub(r'\[\[[^\|\]]+\|([^\]]+)\]\]', r'\1', cast_clean)
    
    our_lead = l['our_value']
    # Check if our lead is in cast_clean
    found = our_lead.lower() in cast_clean.lower()
    state = "MATCH" if found else "DIFFERENT"
    
    print(f"[{l['movie_id']}] {l['movie_title']}")
    print(f"    Our Lead:  {our_lead}")
    print(f"    SWDb Cast: {cast_clean[:120]}...")
    print(f"    State:     {state}\n")
