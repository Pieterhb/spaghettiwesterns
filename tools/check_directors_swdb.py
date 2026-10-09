import json, requests, re

report = json.loads(open('corrections_report.json', encoding='utf-8').read())
cache = json.loads(open('verify_cache.json', encoding='utf-8').read())

dir_issues = [r for r in report if r.get('field') == 'director']
lead_issues = [r for r in report if r.get('field') == 'lead_actor']

print(f"Checking {len(dir_issues)} director issues against actual SWDb wikitext...")

headers = {'User-Agent': 'SpaghettiWesternFactChecker/1.0'}

results = []

for d in dir_issues:
    mid = str(d['movie_id'])
    entry = cache.get(mid, {})
    swdb_entry = entry.get('swdb')
    if not swdb_entry:
        continue
    swdb_title = swdb_entry['swdb_title']
    
    # Fetch wikitext
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
    
    # Extract Director from wikitext
    m = re.search(r'Director:\s*([^\)\n<\|]+)', content, re.IGNORECASE)
    wiki_dir = m.group(1).strip() if m else None
    if not wiki_dir:
        m2 = re.search(r"'''Director[s]?:'''\s*([^\n<]+)", content, re.IGNORECASE)
        wiki_dir = m2.group(1).strip() if m2 else "NOT FOUND IN WIKITEXT"
        
    wiki_dir_clean = re.sub(r'\[\[Category:[^\|\]]+\|([^\]]+)\]\]', r'\1', wiki_dir)
    wiki_dir_clean = re.sub(r'\[\[([^\|\]]+)\]\]', r'\1', wiki_dir_clean)
    wiki_dir_clean = re.sub(r'\[\[[^\|\]]+\|([^\]]+)\]\]', r'\1', wiki_dir_clean)
    
    results.append({
        "id": d['movie_id'],
        "title": d['movie_title'],
        "our_dir": d['our_value'],
        "wiki_title": page.get('title', swdb_title),
        "wiki_dir": wiki_dir_clean
    })

for r in results:
    match = "MATCH" if r['wiki_dir'].lower() in r['our_dir'].lower() or r['our_dir'].lower() in r['wiki_dir'].lower() else "DIFFERENT"
    print(f"[{r['id']}] {r['title']}")
    print(f"    Our:   {r['our_dir']}")
    print(f"    SWDb:  {r['wiki_dir']}")
    print(f"    State: {match}\n")
