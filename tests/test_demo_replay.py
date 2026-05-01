from __future__ import annotations

import os
from pathlib import Path

import pytest

from adapters.demo_replay import DemoReplayAdapter
from demo_fixtures import AUTH_RESCUE_BROKEN, AUTH_RESCUE_CHANGED_FILE, AUTH_RESCUE_FIXED, AUTH_RESCUE_TARGET
from demo_media import build_gif_command, build_record_command, ensure_ffmpeg, media_paths
from demo_replay import DEMOS, bootstrap_env_file, normalized_demo_env, resolve_demo


def test_resolve_demo_returns_runner_path() -> None:
    assert resolve_demo("auth-rescue") == DEMOS["auth-rescue"]


def test_resolve_demo_rejects_unknown_name() -> None:
    with pytest.raises(ValueError):
        resolve_demo("missing-demo")


def test_bootstrap_env_file_copies_example_when_missing(tmp_path: Path) -> None:
    demo_dir = tmp_path / "demo"
    demo_dir.mkdir()
    (demo_dir / ".env.example").write_text("MOCK=1\n", encoding="utf-8")

    env_file = bootstrap_env_file(demo_dir)

    assert env_file == demo_dir / ".env"
    assert env_file.read_text(encoding="utf-8") == "MOCK=1\n"


def test_normalized_demo_env_defaults_to_mock() -> None:
    env = normalized_demo_env({})

    assert env["MOCK"] == "1"


def test_demo_replay_adapter_applies_fixed_state(tmp_path: Path) -> None:
    target = tmp_path / AUTH_RESCUE_TARGET
    target.parent.mkdir(parents=True)
    target.write_text(AUTH_RESCUE_BROKEN, encoding="utf-8")
    adapter = DemoReplayAdapter("auth-rescue")

    result = adapter.run_agent("- ID: task-001\n", str(tmp_path), 30)

    assert result.status == "complete"
    assert result.changed_files == [AUTH_RESCUE_CHANGED_FILE]
    assert target.read_text(encoding="utf-8") == AUTH_RESCUE_FIXED


def test_media_paths_return_expected_outputs() -> None:
    mp4_path, gif_path = media_paths("issue-search")

    assert mp4_path == Path("docs/media/build/issue-search.mp4") or mp4_path.name == "issue-search.mp4"
    assert gif_path.name == "issue-search.gif"


def test_ensure_ffmpeg_fails_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("demo_media.shutil.which", lambda name: None)

    with pytest.raises(RuntimeError, match="ffmpeg"):
        ensure_ffmpeg()


def test_build_record_command_uses_configured_device(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("FFMPEG_VIDEO_DEVICE", "7")

    command = build_record_command("/usr/bin/ffmpeg", tmp_path / "demo.mp4")

    assert command[:6] == ["/usr/bin/ffmpeg", "-y", "-f", "avfoundation", "-framerate", "30"]
    assert command[7] == "7:none"


def test_build_gif_command_targets_output_files(tmp_path: Path) -> None:
    command = build_gif_command("/usr/bin/ffmpeg", tmp_path / "demo.mp4", tmp_path / "demo.gif")

    assert command[0] == "/usr/bin/ffmpeg"
    assert str(tmp_path / "demo.gif") in command
