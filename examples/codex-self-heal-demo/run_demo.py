#!/usr/bin/env python3
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEMO_DIR = ROOT / "examples" / "codex-self-heal-demo"
CONFIG_PATH = DEMO_DIR / "runtime" / "config.json"


BROKEN_BUILD_TASK_BUNDLE = """def build_task_bundle(task, cfg, mission_path, rules_path, progress_path, research_dir):
    mission = read_text(mission_path)
    rules = read_text(rules_path)
    progress = read_text(progress_path)
    research = (
        build_research_summary(task, research_dir)
        if task.get('needs_research') and cfg.get('allow_research')
        else 'Not required.'
    )
    allowed_files = cfg.get('allowed_files', ['mission.md', 'agent-rules.md', 'backlog.json', 'progress.md', 'research/', 'eval/', 'runtime/'])
    bundle = f"# Task Bundle\\n\\n## Task\\n"
    bundle += f"- ID: {task['id']}\\n"
    bundle += f"- Title: {task['title']}\\n"
    bundle += f"- Type: {task['type']}\\n"
    bundle += f"- Priority: {task['priority']}\\n"
    bundle += f"- Risk: {task['risk']}\\n"
    bundle += "\\n## Acceptance criteria\\n"
    for item in task.get('acceptance', []):
        bundle += f"- {item}\\n"
    bundle += "\\n## Allowed files\\n"
    for item in allowed_files:
        bundle += f"- {item}\\n"
    bundle += "\\n## Constraints\\n"
    bundle += "- Work on this task only.\\n"
    bundle += "- Prefer the smallest coherent change.\\n"
    bundle += "- Stop if blocked by ambiguity.\\n"
    bundle += "- Run required validation before completion.\\n"
    bundle += f"\\n## Mission\\n{mission}\\n"
    bundle += f"\\n## Agent rules\\n{rules}\\n"
    bundle += f"\\n## Research summary\\n{research}\\n"
    bundle += f"\\n## Recent progress\\n{progress}\\n"
    return bundle
"""


FIXED_BUILD_TASK_BUNDLE = """def build_task_bundle(task, cfg, mission_path, rules_path, progress_path, research_dir):
    mission = read_text(mission_path)
    rules = read_text(rules_path)
    progress = read_text(progress_path)
    research = (
        build_research_summary(task, research_dir)
        if task.get('needs_research') and cfg.get('allow_research')
        else 'Not required.'
    )
    allowed_files = cfg.get('allowed_files', ['mission.md', 'agent-rules.md', 'backlog.json', 'progress.md', 'research/', 'eval/', 'runtime/'])
    bundle = f"# Task Bundle\\n\\n## Task\\n"
    bundle += f"- ID: {task['id']}\\n"
    bundle += f"- Title: {task['title']}\\n"
    bundle += f"- Type: {task['type']}\\n"
    bundle += f"- Priority: {task['priority']}\\n"
    bundle += f"- Risk: {task['risk']}\\n"
    bundle += "\\n## Acceptance criteria\\n"
    for item in task.get('acceptance', []):
        bundle += f"- {item}\\n"
    validation_commands = get_validation_commands(task, cfg)
    bundle += "\\n## Validation commands\\n"
    for command in validation_commands:
        bundle += f"- {command}\\n"
    bundle += "\\n## Working directory\\n"
    bundle += f"- {cfg.get('working_directory', '.')}\\n"
    bundle += "\\n## Allowed files\\n"
    for item in allowed_files:
        bundle += f"- {item}\\n"
    bundle += "\\n## Constraints\\n"
    bundle += "- Work on this task only.\\n"
    bundle += "- Prefer the smallest coherent change.\\n"
    bundle += "- Stop if blocked by ambiguity.\\n"
    bundle += "- Run required validation before completion.\\n"
    bundle += f"\\n## Mission\\n{mission}\\n"
    bundle += f"\\n## Agent rules\\n{rules}\\n"
    bundle += f"\\n## Research summary\\n{research}\\n"
    bundle += f"\\n## Recent progress\\n{progress}\\n"
    return bundle
"""


BROKEN_RUN_VALIDATION = """def run_validation(commands, run_dir: Path, cwd: Path):
    results = []
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    for idx, cmd in enumerate(commands, start=1):
        proc = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        out_path = run_dir / f'validation-{idx}.txt'
        out_path.write_text(f\"\"\"$ {cmd}

STDOUT:
{proc.stdout}

STDERR:
{proc.stderr}
\"\"\", encoding='utf-8')
        results.append({
            'command': cmd,
            'returncode': proc.returncode,
            'output_file': str(out_path.relative_to(ROOT)),
        })
    return results
"""


FIXED_RUN_VALIDATION = """def run_validation(commands, run_dir: Path, cwd: Path):
    results = []
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    for idx, cmd in enumerate(commands, start=1):
        proc = run_command(cmd, cwd)
        out_path = run_dir / f'validation-{idx}.txt'
        out_path.write_text(f\"\"\"$ {cmd}

STDOUT:
{proc['stdout']}

STDERR:
{proc['stderr']}
\"\"\", encoding='utf-8')
        results.append({
            'command': cmd,
            'returncode': proc['returncode'],
            'output_file': display_path(out_path),
        })
    return results
"""


def _python_bin(repo_root: Path) -> Path:
    candidate = repo_root / ".venv" / "bin" / "python"
    return candidate if candidate.exists() else Path(sys.executable)


def _reset_demo_state(repo_root: Path) -> None:
    backlog_path = repo_root / "examples" / "codex-self-heal-demo" / "backlog.json"
    progress_path = repo_root / "examples" / "codex-self-heal-demo" / "progress.md"
    runtime_runs = repo_root / "runtime" / "runs"
    checkpoints = repo_root / "runtime" / "checkpoints" / "last.json"

    backlog = json.loads(backlog_path.read_text(encoding="utf-8"))
    for task in backlog:
        task["status"] = "todo"
        task["passes"] = False
    backlog_path.write_text(json.dumps(backlog, indent=2) + "\n", encoding="utf-8")
    progress_path.write_text("# Progress Log\n\n<!-- Orchestrator appends entries here after each iteration. -->\n", encoding="utf-8")
    if runtime_runs.exists():
        shutil.rmtree(runtime_runs)
    if checkpoints.exists():
        checkpoints.unlink()


def _reintroduce_regression(repo_root: Path) -> None:
    orchestrator_path = repo_root / "orchestrator.py"
    text = orchestrator_path.read_text(encoding="utf-8")
    if FIXED_BUILD_TASK_BUNDLE not in text or FIXED_RUN_VALIDATION not in text:
        raise RuntimeError("Expected fixed orchestrator implementation was not found.")
    text = text.replace(FIXED_BUILD_TASK_BUNDLE, BROKEN_BUILD_TASK_BUNDLE, 1)
    text = text.replace(FIXED_RUN_VALIDATION, BROKEN_RUN_VALIDATION, 1)
    orchestrator_path.write_text(text, encoding="utf-8")


def _run(cmd, cwd: Path, check: bool) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=check)


def main() -> int:
    temp_root = Path(tempfile.mkdtemp(prefix="orbit-codex-self-heal-"))
    temp_repo = temp_root / "repo"
    shutil.copytree(ROOT, temp_repo, symlinks=True, ignore=shutil.ignore_patterns("runtime/runs"))
    _reset_demo_state(temp_repo)
    _reintroduce_regression(temp_repo)

    python_bin = _python_bin(temp_repo)
    test_cmd = [str(python_bin), "-m", "pytest", "tests/test_orchestrator.py", "-q"]
    before = _run(test_cmd, temp_repo, check=False)
    orbit_cmd = [str(python_bin), "orchestrator.py", "--config", str(CONFIG_PATH.relative_to(ROOT))]
    orbit = _run(orbit_cmd, temp_repo, check=False)
    after = _run(test_cmd, temp_repo, check=False)

    print(f"Temporary repo: {temp_repo}")
    print(f"Before pytest exit: {before.returncode}")
    if before.stdout:
        print(before.stdout.rstrip())
    if before.stderr:
        print(before.stderr.rstrip())
    print("\nOrbit output:")
    if orbit.stdout:
        print(orbit.stdout.rstrip())
    if orbit.stderr:
        print(orbit.stderr.rstrip())
    print(f"\nAfter pytest exit: {after.returncode}")
    if after.stdout:
        print(after.stdout.rstrip())
    if after.stderr:
        print(after.stderr.rstrip())

    backlog = json.loads((temp_repo / "examples" / "codex-self-heal-demo" / "backlog.json").read_text(encoding="utf-8"))
    print("\nFinal backlog:")
    print(json.dumps(backlog, indent=2))

    return 0 if after.returncode == 0 and backlog[0]["status"] == "done" and backlog[0]["passes"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
