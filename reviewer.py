#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def review(run_dir: Path) -> dict:
    evaluation = json.loads((run_dir / 'evaluation.json').read_text(encoding='utf-8'))
    recommendation = 'accept' if evaluation['verdict'] == 'pass' else 'iterate'
    feedback = []
    if not evaluation.get('validation_ok', False):
        feedback.append('Validation failed; fix test or lint issues before acceptance.')
    if evaluation.get('status') != 'complete':
        feedback.append('Implementation did not reach complete status.')
    if not evaluation.get('changed_files'):
        feedback.append('No changed files were reported; verify whether meaningful progress occurred.')
    result = {'recommendation': recommendation, 'feedback': feedback}
    (run_dir / 'review.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    return result


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('run_dir')
    args = ap.parse_args()
    result = review(Path(args.run_dir))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
