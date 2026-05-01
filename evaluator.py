#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def evaluate(run_dir: Path, rubric: dict) -> dict:
    agent_result = json.loads((run_dir / 'agent-result.json').read_text(encoding='utf-8'))
    validation = json.loads((run_dir / 'validation-summary.json').read_text(encoding='utf-8')) if (run_dir / 'validation-summary.json').exists() else []
    task_bundle = (run_dir / 'task-bundle.md').read_text(encoding='utf-8') if (run_dir / 'task-bundle.md').exists() else ''

    validation_ok = all(v.get('returncode', 1) == 0 for v in validation) if validation else True
    changed = len(agent_result.get('changed_files', []))
    status = agent_result.get('status', 'failed')

    scores = {
        'task_focus': rubric.get('task_focus', 1) if '## Task' in task_bundle else 0,
        'validation': rubric.get('validation', 1) if validation_ok else 0,
        'completion': rubric.get('completion', 1) if status == 'complete' else 0,
        'evidence': rubric.get('evidence', 1) if agent_result.get('notes') else 0,
        'change_signal': rubric.get('change_signal', 1) if changed > 0 or status == 'complete' else 0,
    }
    total = sum(scores.values())
    max_score = sum(rubric.values())
    verdict = 'pass' if total >= max_score * 0.8 and validation_ok and status == 'complete' else 'revise'
    result = {
        'verdict': verdict,
        'total': total,
        'max_score': max_score,
        'scores': scores,
        'validation_ok': validation_ok,
        'status': status,
        'changed_files': agent_result.get('changed_files', []),
    }
    (run_dir / 'evaluation.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    return result


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('run_dir')
    args = ap.parse_args()
    rubric = {'task_focus': 2, 'validation': 3, 'completion': 3, 'evidence': 1, 'change_signal': 1}
    result = evaluate(Path(args.run_dir), rubric)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
