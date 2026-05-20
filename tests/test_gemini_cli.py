from types import SimpleNamespace

from adapters.gemini_cli import GeminiCliAdapter


def _proc(stdout="", stderr="", returncode=0):
    return SimpleNamespace(stdout=stdout, stderr=stderr, returncode=returncode)


def test_prepare_prompt_documents_json_contract():
    adapter = GeminiCliAdapter()

    prompt = adapter.prepare_prompt("task bundle")

    assert "respond ONLY with this JSON" in prompt
    assert '"status"' in prompt
    assert '"changed_files"' in prompt
    assert '"metadata"' in prompt


def test_run_agent_uses_gemini_prompt_flag_without_external_credentials(monkeypatch):
    adapter = GeminiCliAdapter()
    calls = []
    stdout = '{"status":"complete","changed_files":["tests/test_gemini_cli.py"],"notes":"added smoke test","metadata":{"adapter":"gemini"}}'

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return _proc(stdout=stdout)

    monkeypatch.setattr("adapters.gemini_cli.subprocess.run", fake_run)

    result = adapter.run_agent("prompt", "/tmp", 30)

    assert calls[0][0] == ["gemini", "-p", "prompt"]
    assert calls[0][1]["cwd"] == "/tmp"
    assert calls[0][1]["timeout"] == 30
    assert result.status == "complete"
    assert result.changed_files == ["tests/test_gemini_cli.py"]
    assert result.notes == "added smoke test"
    assert result.metadata == {"adapter": "gemini"}


def test_run_agent_extracts_final_json_from_gemini_text_output(monkeypatch):
    adapter = GeminiCliAdapter()
    stdout = 'Gemini progress update\n{"status":"blocked","changed_files":[],"notes":"needs config"}'
    monkeypatch.setattr(
        "adapters.gemini_cli.subprocess.run",
        lambda *args, **kwargs: _proc(stdout=stdout),
    )

    result = adapter.run_agent("prompt", "/tmp", 30)

    assert result.status == "blocked"
    assert result.notes == "needs config"


def test_run_agent_returns_failed_for_nonzero_exit(monkeypatch):
    adapter = GeminiCliAdapter()
    monkeypatch.setattr(
        "adapters.gemini_cli.subprocess.run",
        lambda *args, **kwargs: _proc(stdout="", stderr="boom", returncode=1),
    )

    result = adapter.run_agent("prompt", "/tmp", 30)

    assert result.status == "failed"
    assert "non-zero" in result.notes
    assert "boom" in result.raw_output


def test_run_agent_returns_failed_for_invalid_json(monkeypatch):
    adapter = GeminiCliAdapter()
    monkeypatch.setattr(
        "adapters.gemini_cli.subprocess.run",
        lambda *args, **kwargs: _proc(stdout="not json"),
    )

    result = adapter.run_agent("prompt", "/tmp", 30)

    assert result.status == "failed"
    assert "Could not parse Gemini output" in result.notes
