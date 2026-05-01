#!/usr/bin/env python3
import argparse
import importlib
import json
import subprocess
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from evaluator import evaluate
from reviewer import review
from worktree_manager import create_worktree
from budget_manager import can_run, record_run, load_state, save_state, BudgetState
from checkpoint_manager import save_checkpoint, load_checkpoint
from retry_policy import RetryPolicy, should_retry
from observability import emit
from command_runner import run_command, CommandBlockedError
from resume_manager import resume_target
from diff_evaluator import evaluate_diff

ROOT = Path(__file__).resolve().parent
BACKLOG_PATH = ROOT / 'backlog.json'
MISSION_PATH = ROOT / 'mission.md'
RULES_PATH = ROOT / 'agent-rules.md'
PROGRESS_PATH = ROOT / 'progress.md'
RUNTIME_DIR = ROOT / 'runtime'
RUNS_DIR = RUNTIME_DIR / 'runs'
EVAL_DIR = ROOT / 'eval'
RESEARCH_DIR = ROOT / 'research'


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def read_text(path: Path, default: str = '') -> str:
    return path.read_text(encoding='utf-8') if path.exists() else default


def read_json(path: Path, default):
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else default


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def append_progress(path: Path, lines):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as f:
        for line in lines:
            f.write(line.rstrip() + '\n')


def load_config(config_path: Path):
    cfg = read_json(config_path, {})
    cfg.setdefault('mode', 'hitl')
    cfg.setdefault('max_iterations', 1)
    cfg.setdefault('max_wall_clock_minutes', 60)
    cfg.setdefault('max_no_progress_streak', 2)
    cfg.setdefault('require_validation', True)
    cfg.setdefault('allow_research', True)
    cfg.setdefault('validation_commands', [])
    cfg.setdefault('agent_timeout_s', 900)
    cfg.setdefault('auto_checkpoint', True)
    cfg.setdefault('retry_policy', {
        'max_attempts': 2,
        'retry_on_statuses': ['failed'],
        'retry_on_validation_failure': True,
    })
    cfg.setdefault('budgets', {
        'max_runs': 50,
        'max_failures': 10,
        'max_validation_failures': 10,
        'max_estimated_cost_usd': 25.0,
        'estimated_cost_per_run_usd': 0.25,
    })
    cfg.setdefault('agent', {})
    # Support top-level 'adapter' key as alias for agent.adapter
    if 'adapter' in cfg and 'adapter' not in cfg['agent']:
        cfg['agent']['adapter'] = cfg['adapter']
    cfg['agent'].setdefault('adapter', 'adapters.mock:MockAgentAdapter')
    cfg['agent'].setdefault('provider', 'mock')
    return cfg


def resolve_working_directory(cfg) -> Path:
    working_directory = cfg.get('working_directory')
    if not working_directory:
        return ROOT
    return (ROOT / working_directory).resolve()


def get_validation_commands(task, cfg):
    return task.get('validation_commands') or cfg.get('validation_commands', [])


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def choose_task(backlog):
    done = {t['id'] for t in backlog if t['status'] == 'done' and t.get('passes', False)}
    candidates = []
    priority_rank = {'high': 0, 'medium': 1, 'low': 2}
    risk_rank = {'high': 0, 'medium': 1, 'low': 2}
    for task in backlog:
        if task['status'] == 'done':
            continue
        if any(dep not in done for dep in task.get('dependencies', [])):
            continue
        candidates.append(task)
    if not candidates:
        return None
    candidates.sort(key=lambda t: (priority_rank.get(t['priority'], 9), risk_rank.get(t['risk'], 9), t['id']))
    return candidates[0]


def load_adapter(spec: str, adapter_args: dict = None):
    module_name, class_name = spec.split(':', 1)
    module = importlib.import_module(module_name)
    cls = getattr(module, class_name)
    return cls(**(adapter_args or {}))


def build_research_summary(task, research_dir: Path):
    p = research_dir / f"{task['id']}.md"
    if p.exists():
        return read_text(p)
    return 'No task-specific research file exists yet.'


def build_task_bundle(task, cfg, mission_path, rules_path, progress_path, research_dir):
    mission = read_text(mission_path)
    rules = read_text(rules_path)
    progress = read_text(progress_path)
    research = (
        build_research_summary(task, research_dir)
        if task.get('needs_research') and cfg.get('allow_research')
        else 'Not required.'
    )
    allowed_files = cfg.get('allowed_files', ['mission.md', 'agent-rules.md', 'backlog.json', 'progress.md', 'research/', 'eval/', 'runtime/'])
    bundle = f"# Task Bundle\n\n## Task\n"
    bundle += f"- ID: {task['id']}\n"
    bundle += f"- Title: {task['title']}\n"
    bundle += f"- Type: {task['type']}\n"
    bundle += f"- Priority: {task['priority']}\n"
    bundle += f"- Risk: {task['risk']}\n"
    bundle += "\n## Acceptance criteria\n"
    for item in task.get('acceptance', []):
        bundle += f"- {item}\n"
    validation_commands = get_validation_commands(task, cfg)
    bundle += "\n## Validation commands\n"
    for command in validation_commands:
        bundle += f"- {command}\n"
    bundle += "\n## Working directory\n"
    bundle += f"- {cfg.get('working_directory', '.')}\n"
    bundle += "\n## Allowed files\n"
    for item in allowed_files:
        bundle += f"- {item}\n"
    bundle += "\n## Constraints\n"
    bundle += "- Work on this task only.\n"
    bundle += "- Prefer the smallest coherent change.\n"
    bundle += "- Stop if blocked by ambiguity.\n"
    bundle += "- Run required validation before completion.\n"
    bundle += f"\n## Mission\n{mission}\n"
    bundle += f"\n## Agent rules\n{rules}\n"
    bundle += f"\n## Research summary\n{research}\n"
    bundle += f"\n## Recent progress\n{progress}\n"
    return bundle


def run_validation(commands, run_dir: Path, cwd: Path):
    results = []
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    for idx, cmd in enumerate(commands, start=1):
        proc = run_command(cmd, cwd)
        out_path = run_dir / f'validation-{idx}.txt'
        out_path.write_text(f"""$ {cmd}

STDOUT:
{proc['stdout']}

STDERR:
{proc['stderr']}
""", encoding='utf-8')
        results.append({
            'command': cmd,
            'returncode': proc['returncode'],
            'output_file': display_path(out_path),
        })
    return results


def update_task(backlog, task_id, status, passes):
    for task in backlog:
        if task['id'] == task_id:
            task['status'] = (
                'done' if status == 'complete' and passes
                else ('blocked' if status in ['blocked', 'needs_human'] else 'todo')
            )
            task['passes'] = bool(passes and status == 'complete')
            return


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', default='runtime/config.example.json')
    ap.add_argument('--iterations', type=int, default=None)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    cfg = load_config(ROOT / args.config)
    max_iterations = args.iterations or cfg['max_iterations']

    # Support config-overridable file paths
    backlog_path = ROOT / cfg['backlog_file'] if cfg.get('backlog_file') else BACKLOG_PATH
    mission_path = ROOT / cfg['mission_file'] if cfg.get('mission_file') else MISSION_PATH
    rules_path = ROOT / cfg['rules_file'] if cfg.get('rules_file') else RULES_PATH
    progress_path = ROOT / cfg['progress_file'] if cfg.get('progress_file') else PROGRESS_PATH
    research_dir = ROOT / cfg.get('research_dir', 'research')
    runs_dir = RUNS_DIR
    configured_work_cwd = resolve_working_directory(cfg)

    backlog = read_json(backlog_path, [])
    ok, reason = can_run()
    if not ok:
        print(reason)
        sys.exit(2)

    budget_cfg = cfg['budgets']
    state = load_state()
    state.max_runs = budget_cfg.get('max_runs', state.max_runs)
    state.max_failures = budget_cfg.get('max_failures', state.max_failures)
    state.max_validation_failures = budget_cfg.get('max_validation_failures', state.max_validation_failures)
    state.max_estimated_cost_usd = budget_cfg.get('max_estimated_cost_usd', state.max_estimated_cost_usd)
    save_state(state)

    if not backlog:
        print('No backlog found.')
        sys.exit(1)

    adapter = load_adapter(cfg['agent']['adapter'], cfg.get('adapter_args', {}))
    no_progress_streak = 0

    retry_cfg = RetryPolicy(
        max_attempts=cfg['retry_policy'].get('max_attempts', 2),
        retry_on_statuses=tuple(cfg['retry_policy'].get('retry_on_statuses', ['failed'])),
        retry_on_validation_failure=cfg['retry_policy'].get('retry_on_validation_failure', True),
    )

    checkpoint = load_checkpoint()
    if checkpoint:
        emit('resume_detected', checkpoint)

    checkpoint_path = ROOT / 'runtime' / 'checkpoints' / 'last.json'

    for iteration in range(1, max_iterations + 1):
        target = resume_target()
        if target.get('task_id'):
            candidate = next((t for t in backlog if t['id'] == target['task_id']), None)
            # If the resumed/checkpointed task is already done, move on to the next
            if candidate and candidate.get('status') == 'done' and candidate.get('passes', False):
                task = choose_task(backlog)
            else:
                task = candidate
        else:
            task = choose_task(backlog)
        if not task:
            print('All eligible tasks complete.')
            break

        emit('iteration_started', {'iteration': iteration, 'task_id': task['id']})
        runs_dir.mkdir(parents=True, exist_ok=True)
        run_dir = runs_dir / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{task['id']}"
        run_dir.mkdir(parents=True, exist_ok=True)

        bundle = build_task_bundle(task, cfg, mission_path, rules_path, progress_path, research_dir)
        (run_dir / 'task-bundle.md').write_text(bundle, encoding='utf-8')

        work_cwd = create_worktree(task['id']) if cfg.get('use_worktree') else configured_work_cwd
        if cfg.get('use_worktree') and cfg.get('working_directory'):
            work_cwd = work_cwd / cfg['working_directory']

        attempt = 1
        while True:
            emit('attempt_started', {'task_id': task['id'], 'attempt': attempt})

            if args.dry_run:
                result = {
                    'raw_output': bundle,
                    'status': 'complete',
                    'changed_files': [],
                    'notes': 'Dry run only.',
                    'metadata': {'dry_run': 'true'},
                }
            else:
                prompt = adapter.prepare_prompt(bundle)
                result_obj = adapter.run_agent(prompt, str(work_cwd), cfg['agent_timeout_s'])
                result = asdict(result_obj)

            (run_dir / 'agent-result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')

            # Use task-specific validation_commands if defined, otherwise fall back to config
            task_val_cmds = get_validation_commands(task, cfg)
            validation = run_validation(task_val_cmds, run_dir, work_cwd) if cfg['require_validation'] else []
            validation_ok = all(item['returncode'] == 0 for item in validation) if validation else True
            (run_dir / 'validation-summary.json').write_text(json.dumps(validation, indent=2) + '\n', encoding='utf-8')

            if cfg.get('run_evaluator'):
                evaluation = evaluate(run_dir, {'task_focus': 2, 'validation': 3, 'completion': 3, 'evidence': 1, 'change_signal': 1})
            else:
                evaluation = {'verdict': 'pass' if validation_ok else 'revise'}

            if cfg.get('run_reviewer'):
                review_result = review(run_dir)
            else:
                review_result = {'recommendation': 'accept' if evaluation.get('verdict') == 'pass' else 'iterate'}

            diff_result = evaluate_diff(run_dir, work_cwd)

            status = result['status']
            changed_files = result.get('changed_files', [])
            made_progress = status == 'complete' or bool(changed_files)
            no_progress_streak = 0 if made_progress else no_progress_streak + 1

            update_task(backlog, task['id'], status, validation_ok)
            write_json(backlog_path, backlog)

            append_progress(progress_path, [
                '',
                f"## {now_iso()} — {task['id']}",
                f"- Title: {task['title']}",
                f"- Status: {status}",
                f"- Validation passed: {validation_ok}",
                f"- Changed files: {', '.join(changed_files) if changed_files else 'none'}",
                f"- Notes: {result.get('notes', '').strip() or 'none'}",
                f"- Evaluation verdict: {evaluation.get('verdict', 'n/a')}",
                f"- Diff detected: {diff_result.get('has_diff', False)}",
                f"- Diff files estimate: {diff_result.get('files_changed_estimate', 0)}",
                f"- Reviewer recommendation: {review_result.get('recommendation', 'n/a')}",
                f"- Worktree cwd: {work_cwd}",
                f"- Run dir: {display_path(run_dir)}",
            ])

            if cfg.get('auto_checkpoint'):
                if status == 'complete' and validation_ok:
                    # Task succeeded — clear checkpoint so next iteration picks the next task
                    if checkpoint_path.exists():
                        checkpoint_path.unlink()
                else:
                    save_checkpoint({
                        'task_id': task['id'],
                        'iteration': iteration,
                        'attempt': attempt,
                        'run_dir': str(run_dir.relative_to(ROOT)),
                        'status': status,
                    })

            record_run(
                estimated_cost_usd=cfg['budgets'].get('estimated_cost_per_run_usd', 0.25),
                failed=(status == 'failed'),
                validation_failed=(not validation_ok),
            )
            emit('attempt_finished', {
                'task_id': task['id'],
                'attempt': attempt,
                'status': status,
                'validation_ok': validation_ok,
                'evaluation': evaluation.get('verdict'),
                'review': review_result.get('recommendation'),
            })

            if should_retry(status, validation_ok, attempt, retry_cfg):
                attempt += 1
                continue
            break

        if status in ['blocked', 'needs_human', 'failed']:
            print(f"Stopping on status={status} for {task['id']}")
            break
        if no_progress_streak >= cfg['max_no_progress_streak']:
            print('Stopping due to no-progress streak.')
            break

    print('Run finished.')


if __name__ == '__main__':
    main()
