import json
from pathlib import Path

import orchestrator


def test_build_task_bundle_includes_exact_validation_commands(tmp_path):
    mission = tmp_path / "mission.md"
    rules = tmp_path / "rules.md"
    progress = tmp_path / "progress.md"
    research_dir = tmp_path / "research"
    research_dir.mkdir()
    mission.write_text("mission\n", encoding="utf-8")
    rules.write_text("rules\n", encoding="utf-8")
    progress.write_text("progress\n", encoding="utf-8")

    cfg = {
        "allowed_files": ["app/task_manager.py"],
        "validation_commands": ["../../.venv/bin/python -m pytest app/test_task_manager.py -v"],
        "working_directory": "examples/real-e2e-demo",
    }
    task = {
        "id": "task-001",
        "title": "Repair codex path",
        "type": "bugfix",
        "priority": "high",
        "risk": "low",
        "acceptance": ["thing works"],
    }

    bundle = orchestrator.build_task_bundle(task, cfg, mission, rules, progress, research_dir)

    assert "## Validation commands" in bundle
    assert "../../.venv/bin/python -m pytest app/test_task_manager.py -v" in bundle
    assert "## Working directory" in bundle
    assert "examples/real-e2e-demo" in bundle


def test_resolve_working_directory_uses_configured_relative_path():
    cfg = {"working_directory": "examples/real-e2e-demo"}

    cwd = orchestrator.resolve_working_directory(cfg)

    assert cwd == orchestrator.ROOT / "examples/real-e2e-demo"


def test_run_validation_uses_risk_gated_command_runner(tmp_path, monkeypatch):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    calls = []

    def fake_run_command(command, cwd, require_approval=False):
        calls.append((command, cwd, require_approval))
        return {
            "command": command,
            "returncode": 0,
            "stdout": "ok\n",
            "stderr": "",
            "risk_level": "low",
        }

    monkeypatch.setattr(orchestrator, "run_command", fake_run_command)

    results = orchestrator.run_validation(["pytest tests/test_codex_cli.py -v"], run_dir, tmp_path)

    assert calls == [("pytest tests/test_codex_cli.py -v", tmp_path, False)]
    assert results == [
        {
            "command": "pytest tests/test_codex_cli.py -v",
            "returncode": 0,
            "output_file": orchestrator.display_path(run_dir / "validation-1.txt"),
        }
    ]
    assert "STDOUT:\nok" in (run_dir / "validation-1.txt").read_text(encoding="utf-8")


def test_evaluate_and_review_write_expected_artifacts(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "agent-result.json").write_text(
        json.dumps(
            {
                "status": "complete",
                "changed_files": ["adapters/codex_cli.py"],
                "notes": "fixed",
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "validation-summary.json").write_text(
        json.dumps([{"command": "pytest", "returncode": 0}]),
        encoding="utf-8",
    )
    (run_dir / "task-bundle.md").write_text("## Task\n", encoding="utf-8")

    evaluation = orchestrator.evaluate(
        run_dir, {"task_focus": 2, "validation": 3, "completion": 3, "evidence": 1, "change_signal": 1}
    )
    review = orchestrator.review(run_dir)

    assert evaluation["verdict"] == "pass"
    assert review["recommendation"] == "accept"
    assert (run_dir / "evaluation.json").exists()
    assert (run_dir / "review.json").exists()
