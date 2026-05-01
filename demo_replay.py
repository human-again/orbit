from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEMOS = {
    "auth-rescue": ROOT / "examples" / "auth-rescue" / "run_demo.py",
    "issue-search": ROOT / "examples" / "issue-search" / "run_demo.py",
}


def resolve_demo(name: str) -> Path:
    try:
        return DEMOS[name]
    except KeyError as exc:
        options = ", ".join(sorted(DEMOS))
        raise ValueError(f"Unknown demo {name!r}. Expected one of: {options}") from exc


def ensure_prerequisites() -> None:
    if shutil.which("git") is None:
        raise RuntimeError("Missing prerequisite: git")
    if not (ROOT / ".venv" / "bin" / "python").exists() and shutil.which("python3") is None:
        raise RuntimeError("Missing prerequisite: Python 3")


def python_bin() -> Path:
    candidate = ROOT / ".venv" / "bin" / "python"
    if candidate.exists():
        return candidate
    return Path(sys.executable)


def bootstrap_env_file(demo_dir: Path) -> Path | None:
    env_example = demo_dir / ".env.example"
    env_file = demo_dir / ".env"
    if env_example.exists() and not env_file.exists():
        shutil.copyfile(env_example, env_file)
    return env_file if env_file.exists() else None


def normalized_demo_env(env: dict[str, str]) -> dict[str, str]:
    result = dict(env)
    if "MOCK" not in result and "DEMO_ADAPTER" not in result:
        result["MOCK"] = "1"
    return result


def run_demo(name: str, env: dict[str, str] | None = None) -> int:
    ensure_prerequisites()
    runner = resolve_demo(name)
    bootstrap_env_file(runner.parent)
    run_env = normalized_demo_env(env or os.environ)
    cmd = [str(python_bin()), str(runner)]
    proc = subprocess.run(cmd, cwd=ROOT, env=run_env, text=True)
    return proc.returncode


def main(argv: list[str] | None = None) -> int:
    args = list(argv or sys.argv[1:])
    if len(args) != 1:
        print(f"Usage: {Path(sys.argv[0]).name} <demo-name>", file=sys.stderr)
        print(f"Available demos: {', '.join(sorted(DEMOS))}", file=sys.stderr)
        return 2
    try:
        return run_demo(args[0])
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
