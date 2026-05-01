# Phase 3 Notes

This phase adds a three-stage flow:
- Generator: coding agent executes the task.
- Evaluator: separate scoring pass judges output quality.
- Reviewer: converts evaluation into an accept/iterate recommendation.

It also adds:
- Worktree isolation via `git worktree` when available, with directory-copy fallback.
- Provider adapter stubs for Claude CLI, Codex CLI, and Cursor-style CLI wrappers.
- A lightweight HTML dashboard summarizing run results.

## Why this matters
Recent harness guidance emphasizes separating planning, generation, and evaluation, because self-grading is unreliable for long-running work. Worktree isolation also reduces branch conflicts and makes it easier to inspect one run at a time.
