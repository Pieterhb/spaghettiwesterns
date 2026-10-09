import json

report = json.loads(open('corrections_report.json', encoding='utf-8').read())
directors = [r for r in report if r.get('field') == 'director']
leads = [r for r in report if r.get('field') == 'lead_actor']
costars = [r for r in report if r.get('field') == 'co_stars']

print("=== ALL 41 DIRECTOR ISSUES ===")
for d in directors:
    print(f"ID {d['movie_id']}: '{d['movie_title']}' ({d['movie_year']})")
    print(f"   Current: {d['our_value']}")
    print(f"   Source:  {d['source']}")

print("\n=== ALL 25 LEAD ACTOR ISSUES ===")
for l in leads:
    print(f"ID {l['movie_id']}: '{l['movie_title']}' ({l['movie_year']})")
    print(f"   Current: {l['our_value']}")
    print(f"   Source:  {l['source']}")
