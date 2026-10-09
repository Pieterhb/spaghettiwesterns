import requests, json, re

headers = {'User-Agent': 'SpaghettiWesternFactChecker/1.0'}

# Test 5 different films on SWDb
test_titles = [
    "Ace High",
    "Adios Gringo",
    "Arizona Colt",
    "Return of Sabata",
    "Shalako"
]

for t in test_titles:
    resp = requests.get('https://www.spaghetti-western.net/api.php', params={
        'action': 'query',
        'titles': t,
        'prop': 'revisions',
        'rvprop': 'content',
        'rvslots': 'main',
        'format': 'json',
        'redirects': 1
    }, headers=headers, timeout=15)
    data = resp.json()
    pages = data.get('query', {}).get('pages', {})
    page = next(iter(pages.values()))
    title = page.get('title', '')
    content = page.get('revisions', [{}])[0].get('slots', {}).get('main', {}).get('*', '')
    
    print(f"=== {t} -> SWDb Page: {title} ===")
    
    # Extract Director
    dir_match = re.search(r'Director:\s*([^\)\n<\|]+)', content, re.IGNORECASE)
    if dir_match:
        print("  Director:", dir_match.group(1).strip())
    else:
        # try credits section
        dir_match2 = re.search(r"'''Director[s]?:'''\s*([^\n<]+)", content, re.IGNORECASE)
        if dir_match2:
            print("  Director (credits):", dir_match2.group(1).strip())
        else:
            print("  Director: NOT FOUND directly")
            
    # Extract Cast
    cast_match = re.search(r"\*'''Cast'''[^\:]*:\s*([^\n]+)", content, re.IGNORECASE)
    if cast_match:
        print("  Cast:", cast_match.group(1).strip()[:100], "...")
    else:
        print("  Cast: NOT FOUND directly")
        
    # Extract Music
    mus_match = re.search(r"'''Music:'''\s*([^\n<]+)", content, re.IGNORECASE)
    if mus_match:
        print("  Music:", mus_match.group(1).strip())
    print()
