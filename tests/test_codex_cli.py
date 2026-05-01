from types import SimpleNamespace

import pytest

from adapters.codex_cli import CodexCliAdapter


def _proc(stdout="", stderr="", returncode=0):
    return SimpleNamespace(stdout=stdout, stderr=stderr, returncode=returncode)


def test_prepare_prompt_requires_strict_json_output():
    adapter = CodexCliAdapter()

    prompt = adapter.prepare_prompt("task bundle")

    assert "Return ONLY JSON" in prompt
    assert '"status"' in prompt
    assert '"changed_files"' in prompt


def test_run_agent_parses_complete_result_from_jsonl(monkeypatch):
    adapter = CodexCliAdapter()
    stdout = "\n".join(
        [
            '{"type":"thread.started","thread_id":"t1"}',
            '{"type":"item.completed","item":{"type":"agent_message","text":"{\\"status\\":\\"complete\\",\\"changed_files\\":[\\"adapters/codex_cli.py\\"],\\"notes\\":\\"fixed\\",\\"metadata\\":{\\"reasoning_mode\\":\\"concise\\"}}"}}',
            '{"type":"turn.completed"}',
        ]
    )
    monkeypatch.setattr(
        "adapters.codex_cli.subprocess.run",
        lambda *args, **kwargs: _proc(stdout=stdout),
    )

    result = adapter.run_agent("prompt", "/tmp", 30)

    assert result.status == "complete"
    assert result.changed_files == ["adapters/codex_cli.py"]
    assert result.notes == "fixed"
    assert result.metadata == {"reasoning_mode": "concise"}


def test_run_agent_accepts_blocked_status(monkeypatch):
    adapter = CodexCliAdapter()
    stdout = '{"type":"item.completed","item":{"type":"agent_message","text":"{\\"status\\":\\"blocked\\",\\"changed_files\\":[],\\"notes\\":\\"need pytest\\"}"}}'
    monkeypatch.setattr(
        "adapters.codex_cli.subprocess.run",
        lambda *args, **kwargs: _proc(stdout=stdout),
    )

    result = adapter.run_agent("prompt", "/tmp", 30)

    assert result.status == "blocked"
    assert result.notes == "need pytest"


def test_run_agent_uses_last_agent_message_when_codex_emits_progress_updates(monkeypatch):
    adapter = CodexCliAdapter()
    stdout = "\n".join(
        [
            '{"type":"item.completed","item":{"type":"agent_message","text":"I am inspecting the repo now."}}',
            '{"type":"item.completed","item":{"type":"agent_message","text":"{\\"status\\":\\"complete\\",\\"changed_files\\":[\\"orchestrator.py\\"],\\"notes\\":\\"done\\"}"}}',
        ]
    )
    monkeypatch.setattr(
        "adapters.codex_cli.subprocess.run",
        lambda *args, **kwargs: _proc(stdout=stdout),
    )

    result = adapter.run_agent("prompt", "/tmp", 30)

    assert result.status == "complete"
    assert result.changed_files == ["orchestrator.py"]
    assert result.notes == "done"


def test_run_agent_returns_failed_for_nonzero_exit(monkeypatch):
    adapter = CodexCliAdapter()
    monkeypatch.setattr(
        "adapters.codex_cli.subprocess.run",
        lambda *args, **kwargs: _proc(stdout="", stderr="boom", returncode=1),
    )

    result = adapter.run_agent("prompt", "/tmp", 30)

    assert result.status == "failed"
    assert "non-zero" in result.notes
    assert "boom" in result.raw_output


def test_run_agent_returns_failed_when_final_message_missing(monkeypatch):
    adapter = CodexCliAdapter()
    stdout = '{"type":"thread.started","thread_id":"t1"}\n{"type":"turn.completed"}'
    monkeypatch.setattr(
        "adapters.codex_cli.subprocess.run",
        lambda *args, **kwargs: _proc(stdout=stdout),
    )

    result = adapter.run_agent("prompt", "/tmp", 30)

    assert result.status == "failed"
    assert "final agent message" in result.notes


def test_run_agent_returns_failed_for_invalid_final_json(monkeypatch):
    adapter = CodexCliAdapter()
    stdout = '{"type":"item.completed","item":{"type":"agent_message","text":"not json"}}'
    monkeypatch.setattr(
        "adapters.codex_cli.subprocess.run",
        lambda *args, **kwargs: _proc(stdout=stdout),
    )

    result = adapter.run_agent("prompt", "/tmp", 30)

    assert result.status == "failed"
    assert "Could not parse" in result.notes


def test_run_agent_returns_failed_for_empty_output(monkeypatch):
    adapter = CodexCliAdapter()
    monkeypatch.setattr(
        "adapters.codex_cli.subprocess.run",
        lambda *args, **kwargs: _proc(stdout=""),
    )

    result = adapter.run_agent("prompt", "/tmp", 30)

    assert result.status == "failed"
    assert "final agent message" in result.notes
