# Progress Log

## 2026-04-26
- Initialized scaffold.
- Added mission, rules, backlog, and templates.
- Next step: implement `task-001` with a minimal orchestrator.

## 2026-04-29
- Task id: codex-self-heal-demo
- Changed: hardened `adapters/codex_cli.py`, aligned orchestrator validation/runtime behavior, added regression tests, and added a temp-copy Codex self-heal demo under `examples/codex-self-heal-demo/`.
- Validation: `.venv/bin/python -m pytest tests/test_codex_cli.py tests/test_orchestrator.py examples/real-e2e-demo/app/test_task_manager.py -q` passed (22 tests); `.venv/bin/python examples/codex-self-heal-demo/run_demo.py` completed with the temp-copy backlog at `done/passes=true` and run artifacts showing `evaluation.json verdict=pass` and `review.json recommendation=accept`.
- Risks: the live Codex run still emits verbose progress messages and CLI warnings into the adapter raw output, so the adapter now intentionally parses the last agent message instead of assuming a single response frame.
- Next step: if you want a shorter GitHub demo loop, trim the Codex self-heal mission prompt and reduce plugin/skill noise in the captured run output.

## 2026-04-29
- Task id: fast-ship-demo-refresh
- Changed: added `auth-rescue` and `issue-search` temp-copy demos, a deterministic `adapters.demo_replay:DemoReplayAdapter`, shared `replay.sh` and `demo_replay.py` entrypoints, the separate `scripts/make-demo-media.sh` / `demo_media.py` media workflow, placeholder GIF assets under `docs/media/`, and README/demo documentation for the new primary launch path.
- Validation: `.venv/bin/python -m pytest tests/test_demo_replay.py tests/test_codex_cli.py tests/test_orchestrator.py examples/auth-rescue/tests/auth/test_auth_flow.py examples/issue-search/tests/test_issue_search.py -q` passed (27 tests); `./replay.sh auth-rescue` and `./replay.sh issue-search` both completed with temp-copy backlogs at `done/passes=true`; `scripts/make-demo-media.sh auth-rescue` failed as expected with `Missing prerequisite: ffmpeg`.
- Risks: the checked-in GIF files are placeholders because `ffmpeg` is not installed in this environment, so real launch captures still need to be generated on a machine with `ffmpeg` available.
- Next step: run `scripts/make-demo-media.sh auth-rescue` and `scripts/make-demo-media.sh issue-search` on a workstation with `ffmpeg`, then replace the placeholder GIFs with the real captures.

## 2026-04-29
- Task id: generate-demo-media
- Changed: rewrote `demo_media.py` to use Pillow for headless terminal-style GIF generation (no screen capture required); added `orchestrator-pseudocode` as a third supported demo; installed `pillow` into `.venv`; generated all three real GIFs: `docs/media/auth-rescue.gif`, `docs/media/issue-search.gif`, `docs/media/orchestrator-pseudocode.gif`.
- Validation: `pytest tests/test_demo_replay.py -q` — 9 passed; all three GIFs verified visually (dark background, correct color scheme, text visible).
- Risks: `ffmpeg`'s `drawtext` filter is not available in this Homebrew build (no libfreetype); the Pillow-based approach is the primary path and the `--screen-capture` flag retains the avfoundation path for future use.
- Next step: add `orchestrator-pseudocode` GIF reference to README if desired.

## 2026-05-20
- Task id: community-readiness
- Changed: added a standard MIT `LICENSE`, code of conduct, GitHub issue forms, PR template, and documented good first contribution lanes.
- Validation: `git diff --check` passed; `.venv/bin/pytest tests/ -q` passed locally with 21 tests.
- Risks: local validation used the available system Python 3.9 virtualenv even though the project declares Python 3.11+; GitHub CI remains configured for Python 3.11, 3.12, and 3.13.
- Next step: open starter `good first issue` / `help wanted` issues for adapters, mission templates, demos, docs, and validation fixtures.

## 2026-05-20
- Task id: tiny-landing-page
- Changed: added a no-build static landing page at `docs/index.html`, using the supplied Orbit hero image at `docs/media/orbit.png`, and linked it from the README.
- Validation: `git diff --check` passed; `.venv/bin/pytest tests/ -q` passed with 21 tests; local static server returned HTTP 200 for `/` and `/media/orbit.png`; browser smoke test passed at desktop and mobile sizes with no console warnings or errors.
- Risks: GitHub Pages still needs to be enabled for the `/docs` folder in repository settings before the page has a public URL.
- Next step: enable GitHub Pages for the `/docs` folder after the PR merges.
