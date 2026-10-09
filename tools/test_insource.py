import requests

headers = {'User-Agent': 'SpaghettiWesternFactChecker/1.0'}
resp = requests.get('https://www.spaghetti-western.net/api.php', params={
    'action': 'query',
    'list': 'search',
    'srsearch': 'insource:"Also known as" "Kill Johnny Ringo"',
    'format': 'json'
}, headers=headers, timeout=10)
data = resp.json()
print('Insource search:')
for r in data.get('query', {}).get('search', [])[:5]:
    print(' ', r['title'])
