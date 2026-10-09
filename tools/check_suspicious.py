import json

report = json.loads(open('corrections_report.json', encoding='utf-8').read())
suspicious_ids = [92, 118, 231, 234, 474, 524, 554, 2, 38, 179, 205, 355]

for issue in report:
    if issue['movie_id'] in suspicious_ids and issue['field'] == 'year':
        print(f"ID {issue['movie_id']}: {issue['movie_title']}")
        print(f"  Ours: {issue['our_value']}  ->  Ref: {issue['reference_value']}")
        print(f"  Confidence: {issue['confidence']}")
        print(f"  Source: {issue['source']}")
        print(f"  Note: {issue['note'][:120]}")
        print()
