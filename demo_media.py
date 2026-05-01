from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MEDIA_DIR = ROOT / "docs" / "media"
BUILD_DIR = MEDIA_DIR / "build"
SUPPORTED_DEMOS = {"auth-rescue", "issue-search", "orchestrator-pseudocode"}

# --------------------------------------------------------------------------- #
# Screen-capture helpers (macOS avfoundation — requires display + permissions) #
# --------------------------------------------------------------------------- #


def ensure_ffmpeg() -> str:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError("Missing prerequisite: ffmpeg")
    return ffmpeg


def media_paths(demo_name: str) -> tuple[Path, Path]:
    if demo_name not in SUPPORTED_DEMOS:
        raise ValueError(f"Unsupported demo {demo_name!r}")
    return BUILD_DIR / f"{demo_name}.mp4", MEDIA_DIR / f"{demo_name}.gif"


def build_record_command(ffmpeg: str, mp4_path: Path) -> list[str]:
    video_device = os.environ.get("FFMPEG_VIDEO_DEVICE", "1")
    return [
        ffmpeg,
        "-y",
        "-f",
        "avfoundation",
        "-framerate",
        "30",
        "-i",
        f"{video_device}:none",
        "-pix_fmt",
        "yuv420p",
        str(mp4_path),
    ]


def build_gif_command(ffmpeg: str, mp4_path: Path, gif_path: Path) -> list[str]:
    palette = BUILD_DIR / f"{mp4_path.stem}-palette.png"
    return [
        ffmpeg,
        "-y",
        "-i",
        str(mp4_path),
        "-i",
        str(palette),
        "-lavfi",
        "fps=12,scale=1440:-1:flags=lanczos[x];[x][1:v]paletteuse",
        str(gif_path),
    ]


def build_palette_command(ffmpeg: str, mp4_path: Path) -> list[str]:
    palette = BUILD_DIR / f"{mp4_path.stem}-palette.png"
    return [
        ffmpeg,
        "-y",
        "-i",
        str(mp4_path),
        "-vf",
        "fps=12,scale=1440:-1:flags=lanczos,palettegen",
        str(palette),
    ]


def run_media_capture(demo_name: str) -> int:
    ffmpeg = ensure_ffmpeg()
    mp4_path, gif_path = media_paths(demo_name)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)

    env = dict(os.environ)
    env["OPEN_BROWSER"] = "1"
    env["RECORD_MEDIA"] = "1"

    replay_cmd = [str(ROOT / "replay.sh"), demo_name]
    replay_proc = subprocess.Popen(replay_cmd, cwd=ROOT, env=env, text=True)
    record_proc = subprocess.Popen(build_record_command(ffmpeg, mp4_path), cwd=ROOT)

    replay_code = replay_proc.wait()
    record_proc.terminate()
    record_proc.wait(timeout=10)
    if replay_code != 0:
        return replay_code

    palette_cmd = build_palette_command(ffmpeg, mp4_path)
    palette_proc = subprocess.run(palette_cmd, cwd=ROOT, text=True, capture_output=True)
    if palette_proc.returncode != 0:
        raise RuntimeError(palette_proc.stderr or "ffmpeg failed while generating the palette")
    gif_proc = subprocess.run(build_gif_command(ffmpeg, mp4_path, gif_path), cwd=ROOT, text=True, capture_output=True)
    if gif_proc.returncode != 0:
        raise RuntimeError(gif_proc.stderr or "ffmpeg failed while generating GIF")
    print(f"Wrote {mp4_path.relative_to(ROOT)}")
    print(f"Wrote {gif_path.relative_to(ROOT)}")
    return 0


# --------------------------------------------------------------------------- #
# Headless text-based GIF generation via Pillow frame rendering               #
# --------------------------------------------------------------------------- #

_FONT_CANDIDATES = [
    "/System/Library/Fonts/Monaco.ttf",
    "/System/Library/Fonts/Supplemental/Courier New.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
]

_COLORS = {
    "normal": (230, 237, 243),
    "cmd":    (121, 192, 255),
    "ok":     (126, 231, 135),
    "err":    (248,  81,  73),
    "dim":    (132, 141, 151),
    "kw":     (255, 123, 114),
}

_BG = (13, 17, 23)
_FONT_SIZE = 16
_LINE_H = 24
_PAD_X = 28
_PAD_Y = 24
_GIF_W = 860
_FPS = 12
_LINE_INTERVAL = 0.42
_HOLD = 2.5

# Each script is a list of (style, text) pairs; style is a key in _COLORS.
_SCRIPTS: dict[str, list[tuple[str, str]]] = {
    "auth-rescue": [
        ("cmd",    "$ ./replay.sh auth-rescue"),
        ("dim",    ""),
        ("dim",    "[orbit] loading mission ..."),
        ("dim",    "[orbit] backlog: 1 task ready"),
        ("normal", "[orbit] task: fix-auth-lookup"),
        ("dim",    ""),
        ("err",    "[before] pytest -- 3 FAILED"),
        ("dim",    "  test_authenticate_accepts_case_insensitive_email"),
        ("dim",    "  test_authenticate_ignores_surrounding_whitespace"),
        ("dim",    "  test_issue_session_label_uses_canonical_email"),
        ("dim",    ""),
        ("normal", "[orbit] agent: applying fix ..."),
        ("ok",     "  + _normalize_email: strip + casefold"),
        ("ok",     "  + find_user_by_email: case-insensitive match"),
        ("ok",     "  + issue_session_label: canonical email"),
        ("dim",    ""),
        ("ok",     "[after]  pytest -- 3 passed"),
        ("ok",     "[orbit] evaluation: score 4/4 -- pass"),
        ("ok",     "[orbit] review: accept"),
        ("ok",     "[orbit] mission complete."),
    ],
    "issue-search": [
        ("cmd",    "$ ./replay.sh issue-search"),
        ("dim",    ""),
        ("dim",    "[orbit] loading mission ..."),
        ("dim",    "[orbit] backlog: 1 task ready"),
        ("normal", "[orbit] task: add-issue-search"),
        ("dim",    ""),
        ("err",    "[before] pytest -- 2 FAILED"),
        ("dim",    "  test_filter_issues_by_keyword"),
        ("dim",    "  test_filter_issues_returns_empty_for_no_match"),
        ("dim",    ""),
        ("normal", "[orbit] agent: applying fix ..."),
        ("ok",     "  + filter_issues: keyword search in title"),
        ("ok",     "  + render_dashboard: empty-results path"),
        ("dim",    ""),
        ("ok",     "[after]  pytest -- 4 passed"),
        ("ok",     "[orbit] evaluation: score 4/4 -- pass"),
        ("ok",     "[orbit] review: accept"),
        ("ok",     "[orbit] mission complete."),
    ],
    "orchestrator-pseudocode": [
        ("kw",     "# orbit orchestration loop"),
        ("dim",    ""),
        ("normal", "load mission, rules, backlog, progress"),
        ("normal", "load config"),
        ("normal", "for iteration in 1..max_iterations:"),
        ("normal", "  choose highest-priority task"),
        ("dim",    "         (dependencies must be complete)"),
        ("normal", "  if no task remains: stop success"),
        ("normal", "  build task bundle"),
        ("normal", "  if task.needs_research and allow_research:"),
        ("normal", "    create or refresh research brief"),
        ("normal", "  prompt = adapter.prepare_prompt(task_bundle)"),
        ("normal", "  result = adapter.run_agent(prompt, ...)"),
        ("normal", "  run validation commands"),
        ("normal", "  write eval outputs"),
        ("normal", "  update backlog status"),
        ("normal", "  append note to progress.md"),
        ("normal", "  if result.status in [blocked, failed]: stop"),
        ("normal", "  if no progress streak: stop"),
        ("normal", "end"),
    ],
}


def _find_font() -> str:
    for path in _FONT_CANDIDATES:
        if Path(path).exists():
            return path
    raise RuntimeError(
        "No suitable monospace font found. "
        f"Expected one of: {', '.join(_FONT_CANDIDATES)}"
    )


def _render_frames(script: list[tuple[str, str]], font_path: str) -> list:
    """
    Return a list of (frame, hold_frames) tuples.
    Each state adds one new line; hold_frames is how long to show that state.
    Requires Pillow.
    """
    from PIL import Image, ImageDraw, ImageFont

    font = ImageFont.truetype(font_path, _FONT_SIZE)
    height = _PAD_Y + len(script) * _LINE_H + _PAD_Y

    hold_per_line = max(1, round(_LINE_INTERVAL * _FPS))
    hold_last = max(1, round(_HOLD * _FPS))

    frames: list[tuple[Image.Image, int]] = []
    for visible_count in range(1, len(script) + 1):
        img = Image.new("RGB", (_GIF_W, height), _BG)
        draw = ImageDraw.Draw(img)
        for i in range(visible_count):
            style, text = script[i]
            if not text:
                continue
            color = _COLORS.get(style, _COLORS["normal"])
            y = _PAD_Y + i * _LINE_H
            draw.text((_PAD_X, y), text, font=font, fill=color)
        hold = hold_last if visible_count == len(script) else hold_per_line
        frames.append((img, hold))

    return frames


def _frames_to_gif(frames: list, gif_path: Path) -> None:
    """Save Pillow frames as an animated GIF with the given per-frame durations."""
    from PIL import Image

    images: list[Image.Image] = []
    durations: list[int] = []
    for img, hold_frames in frames:
        images.append(img)
        durations.append(round(hold_frames * 1000 / _FPS))

    if not images:
        raise RuntimeError("No frames to write")

    images[0].save(
        gif_path,
        format="GIF",
        save_all=True,
        append_images=images[1:],
        duration=durations,
        loop=0,
        optimize=False,
    )


def run_text_gif(demo_name: str) -> int:
    if demo_name not in _SCRIPTS:
        raise ValueError(
            f"No text script for {demo_name!r}. "
            f"Available: {', '.join(sorted(_SCRIPTS))}"
        )
    font = _find_font()
    _, gif_path = media_paths(demo_name)
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)

    script = _SCRIPTS[demo_name]
    frames = _render_frames(script, font)
    _frames_to_gif(frames, gif_path)
    print(f"Wrote {gif_path.relative_to(ROOT)}")
    return 0


# --------------------------------------------------------------------------- #
# Entry point                                                                  #
# --------------------------------------------------------------------------- #


def main(argv: list[str] | None = None) -> int:
    args = list(argv or sys.argv[1:])
    if not (1 <= len(args) <= 2):
        print("Usage: python -m demo_media <demo-name> [--screen-capture]", file=sys.stderr)
        return 2
    demo_name = args[0]
    screen_capture = "--screen-capture" in args or os.environ.get("SCREEN_CAPTURE") == "1"
    try:
        if screen_capture:
            return run_media_capture(demo_name)
        return run_text_gif(demo_name)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
