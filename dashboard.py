#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / 'runtime' / 'runs'
OUT = ROOT / 'runtime' / 'dashboard.html'

rows = []
if RUNS.exists():
    for run_dir in sorted(RUNS.iterdir()):
        if not run_dir.is_dir():
            continue
        result = {}
        evaluation = {}
        review = {}
        if (run_dir / 'agent-result.json').exists():
            result = json.loads((run_dir / 'agent-result.json').read_text(encoding='utf-8'))
        if (run_dir / 'evaluation.json').exists():
            evaluation = json.loads((run_dir / 'evaluation.json').read_text(encoding='utf-8'))
        if (run_dir / 'review.json').exists():
            review = json.loads((run_dir / 'review.json').read_text(encoding='utf-8'))
        rows.append({
            'run': run_dir.name,
            'status': result.get('status', ''),
            'changed_files': ', '.join(result.get('changed_files', [])),
            'verdict': evaluation.get('verdict', ''),
            'recommendation': review.get('recommendation', ''),
        })

html = ['<!doctype html><html><head><meta charset="utf-8"><title>Agent Runs Dashboard</title><style>body{font-family:Arial,sans-serif;margin:24px}table{border-collapse:collapse;width:100%}th,td{border:1px solid #ccc;padding:8px;text-align:left}th{background:#f3f3f3}</style></head><body>']
html.append('<h1>Agent Runs Dashboard</h1>')
html.append('<table><thead><tr><th>Run</th><th>Status</th><th>Changed Files</th><th>Verdict</th><th>Recommendation</th></tr></thead><tbody>')
for r in rows:
    html.append(f"<tr><td>{r['run']}</td><td>{r['status']}</td><td>{r['changed_files']}</td><td>{r['verdict']}</td><td>{r['recommendation']}</td></tr>")
html.append('</tbody></table></body></html>')
OUT.write_text(''.join(html), encoding='utf-8')
print(str(OUT))
