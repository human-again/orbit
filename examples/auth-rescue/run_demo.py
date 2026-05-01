#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from demo_fixtures import AUTH_RESCUE_BROKEN, AUTH_RESCUE_FIXED, AUTH_RESCUE_TARGET


DEMO_DIR = ROOT / "examples" / "auth-rescue"
CONFIG_PATH = DEMO_DIR / "runtime" / "config.json"
REAL_ADAPTERS = {
    "codex": {
        "adapter": "adapters.codex_cli:CodexCliAdapter",
        "adapter_args": {
            "command": "codex",
            "args": ["exec", "--skip-git-repo-check", "--ephemeral", "--json", "--dangerously-bypass-approvals-and-sandbox"],
        },
    },
    "claude": {
        "adapter": "adapters.claude_cli:ClaudeCliAdapter",
        "adapter_args": {
            "command": "claude",
            "args": ["--print", "--output-format", "json", "--dangerously-skip-permissions"],
        },
    },
    "cursor": {
        "adapter": "adapters.cursor_cli:CursorCliAdapter",
        "adapter_args": {"command": "cursor-agent", "args": []},
    },
}


def _python_bin(repo_root: Path) -> Path:
    candidate = repo_root / ".venv" / "bin" / "python"
    return candidate if candidate.exists() else Path(sys.executable)


def _run(cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, env=env, text=True, capture_output=True, check=False)


def _reset_demo_state(repo_root: Path) -> None:
    backlog_path = repo_root / "examples" / "auth-rescue" / "backlog.json"
    progress_path = repo_root / "examples" / "auth-rescue" / "progress.md"
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
    target = repo_root / "examples" / "auth-rescue" / AUTH_RESCUE_TARGET
    text = target.read_text(encoding="utf-8")
    if text != AUTH_RESCUE_FIXED:
        raise RuntimeError("Auth rescue demo is not in the expected fixed state.")
    target.write_text(AUTH_RESCUE_BROKEN, encoding="utf-8")


def _write_runtime_override(repo_root: Path) -> Path:
    base_config = json.loads((repo_root / CONFIG_PATH.relative_to(ROOT)).read_text(encoding="utf-8"))
    adapter_name = os.environ.get("DEMO_ADAPTER", "").strip().lower()
    if not adapter_name:
        return CONFIG_PATH.relative_to(ROOT)
    if adapter_name not in REAL_ADAPTERS:
        valid = ", ".join(sorted(REAL_ADAPTERS))
        raise RuntimeError(f"Unsupported DEMO_ADAPTER value {adapter_name!r}. Expected one of: {valid}")
    base_config.update(REAL_ADAPTERS[adapter_name])
    override_path = repo_root / "runtime" / "generated-auth-rescue-config.json"
    override_path.write_text(json.dumps(base_config, indent=2) + "\n", encoding="utf-8")
    return override_path.relative_to(repo_root)


def _build_report(temp_repo: Path, run_dir: Path) -> Path:
    report_path = temp_repo / "examples" / "auth-rescue" / "report.html"
    evaluation = json.loads((run_dir / "evaluation.json").read_text(encoding="utf-8"))
    review = json.loads((run_dir / "review.json").read_text(encoding="utf-8"))
    validation = json.loads((run_dir / "validation-summary.json").read_text(encoding="utf-8"))
    report_path.write_text(
        f"""<!doctype html>
<html lang="en">
  <head><meta charset="utf-8"><title>Auth Rescue Report</title></head>
  <body style="font-family:Helvetica,Arial,sans-serif;padding:2rem;background:#f7f4ee">
    <h1>Auth Rescue Mission Report</h1>
    <p>Evaluation verdict: <strong>{evaluation['verdict']}</strong></p>
    <p>Reviewer recommendation: <strong>{review['recommendation']}</strong></p>
    <pre>{json.dumps(validation, indent=2)}</pre>
  </body>
</html>
""",
        encoding="utf-8",
    )
    return report_path


def main() -> int:
    temp_root = Path(tempfile.mkdtemp(prefix="orbit-auth-rescue-"))
    temp_repo = temp_root / "repo"
    shutil.copytree(ROOT, temp_repo, symlinks=True, ignore=shutil.ignore_patterns("runtime/runs"))
    _reset_demo_state(temp_repo)
    _reintroduce_regression(temp_repo)

    python_bin = _python_bin(temp_repo)
    env = dict(os.environ)
    config_path = _write_runtime_override(temp_repo)
    test_cmd = [str(python_bin), "-m", "pytest", "tests/auth", "-q"]
    before = _run(test_cmd, temp_repo / "examples" / "auth-rescue", env=env)
    orbit_cmd = [str(python_bin), "orchestrator.py", "--config", str(config_path)]
    orbit = _run(orbit_cmd, temp_repo, env=env)
    after = _run(test_cmd, temp_repo / "examples" / "auth-rescue", env=env)

    run_dirs = sorted((temp_repo / "runtime" / "runs").glob("*task-001"))
    latest_run = run_dirs[-1] if run_dirs else None

    print(f"Temporary repo: {temp_repo}")
    print(f"Demo mode: {'mock' if env.get('MOCK', '1') == '1' and not env.get('DEMO_ADAPTER') else env.get('DEMO_ADAPTER', 'custom')}")
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

    if latest_run is not None:
        print(f"\nArtifacts: {latest_run}")
        print(f"- {latest_run / 'agent-result.json'}")
        print(f"- {latest_run / 'evaluation.json'}")
        print(f"- {latest_run / 'review.json'}")
        print(f"- {latest_run / 'validation-summary.json'}")
        if env.get("OPEN_BROWSER") == "1":
            webbrowser.open(_build_report(temp_repo, latest_run).as_uri())

    backlog = json.loads((temp_repo / "examples" / "auth-rescue" / "backlog.json").read_text(encoding="utf-8"))
    print("\nFinal backlog:")
    print(json.dumps(backlog, indent=2))
    return 0 if after.returncode == 0 and backlog[0]["status"] == "done" and backlog[0]["passes"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
