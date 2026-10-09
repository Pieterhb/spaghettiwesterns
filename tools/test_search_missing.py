import requests

headers = {'User-Agent': 'SpaghettiWesternFactChecker/1.0'}
titles = [
    'Kill Johnny Ringo',
    'Lemonade Joe',
    "Let's Go and Kill Sartana",
    'Long Ride from Hell',
    'Left Handed Johnny West',
    'Man Who Cried for Revenge',
    'Man Who Killed Billy the Kid'
]

for t in titles:
    resp = requests.get('https://www.spaghetti-western.net/api.php', params={
        'action': 'query',
        'list': 'search',
        'srsearch': f'"{t}"',
        'format': 'json'
    }, headers=headers, timeout=10)
    data = resp.json()
    res = [r['title'] for r in data.get('query', {}).get('search', [])[:2]]
    print(f"{t:30} -> {res}")
