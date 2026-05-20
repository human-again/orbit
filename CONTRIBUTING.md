# Contributing to Orbit

Thanks for your interest. Orbit is intentionally small — contributions that keep it small and correct are the most welcome.

## What we want

- **New adapters** — wrapping a new agent CLI? Add a file in `adapters/` following the `BaseAgentAdapter` contract in `adapters/base.py`.
- **New mission templates** — a real-world scenario that shows Orbit solving a common problem. Add it to `missions/` with a `mission.md` and `backlog.json`.
- **New demo examples** — runnable end-to-end demos for `examples/`. Follow the pattern in `examples/auth-rescue/`.
- **Bug fixes** — especially around validation, retry logic, or checkpoint resumability.
- **Documentation improvements** — clearer quickstart, better examples.

## Good first contribution lanes

If you are new to Orbit, the safest places to start are:

- **Adapter smoke tests** — add coverage for an existing adapter's command shape, status parsing, or failure behavior.
- **Mission templates** — add a small, realistic `missions/<scenario>/` folder with `mission.md` and `backlog.json`.
- **Demo polish** — improve one deterministic replay demo without adding external services or secrets.
- **Docs examples** — clarify one workflow with exact commands and expected artifact paths.
- **Validation fixtures** — add a narrow test for validation, retry, checkpoint, budget, or review behavior.

Good first issues should include:

- the file or folder to change,
- the expected validation command,
- the artifact or behavior that proves completion,
- any scope boundaries that should not be crossed.

## What we don't want (yet)

- New dependencies beyond stdlib + `pytest` + `pillow`
- UI or web dashboard (tracked for a future milestone)
- Changes to the adapter contract without an issue discussion first

## How to run tests

```bash
python -m venv .venv && .venv/bin/pip install pytest pillow
.venv/bin/pytest tests/ -q
```

All 21 tests should pass. If you're adding a new adapter or feature, add tests in `tests/`.

## Try the demos (no API key needed)

```bash
MOCK=1 ./replay.sh auth-rescue
MOCK=1 ./replay.sh issue-search
```

## Submitting a PR

1. Fork the repo and create a branch from `master`.
2. Make your change with tests.
3. Run `pytest tests/ -q` — must pass.
4. Open a PR with a clear description: what changed, why, and what you tested.

Questions? Open a GitHub Issue — we read them all.
