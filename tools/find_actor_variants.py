import csv, collections
from difflib import SequenceMatcher

with open('Complete_Westerns.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

actors = collections.Counter()
actor_movies = collections.defaultdict(list)

for idx, r in enumerate(rows):
    mid = idx + 1
    title = r['Title']
    lead = r['Lead_Actor'].strip()
    if lead:
        actors[lead] += 1
        actor_movies[lead].append((mid, title, 'Lead'))
    cs_list = [c.strip() for c in r['Co_Stars'].split(',') if c.strip()]
    for c in cs_list:
        actors[c] += 1
        actor_movies[c].append((mid, title, 'Co-Star'))

names = sorted(actors.keys())
print(f"Total unique actor entries: {len(names)}")

similar_pairs = []
for i in range(len(names)):
    for j in range(i+1, len(names)):
        n1 = names[i]
        n2 = names[j]
        # Ignore exact substring parentheticals like "Jack Betts" vs "Jack Betts (as Hunt Powers)"
        if '(' in n1 or '(' in n2 or '[' in n1 or '[' in n2:
            continue
        if len(n1) < 5 or len(n2) < 5:
            continue
        ratio = SequenceMatcher(None, n1.lower(), n2.lower()).ratio()
        if 0.85 <= ratio < 1.0:
            similar_pairs.append((n1, actors[n1], n2, actors[n2], ratio))

similar_pairs.sort(key=lambda x: -x[4])
print(f"\nTop 50 highly similar name pairs (potential spelling mistakes/variants):")
for p in similar_pairs[:50]:
    print(f"  {p[0]} ({p[1]}x) <==> {p[2]} ({p[3]}x) [sim: {p[4]:.2f}]")
