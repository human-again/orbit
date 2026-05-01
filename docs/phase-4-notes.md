# Phase 4 Notes

This phase hardens the scaffold for longer unattended runs.

## Added capabilities
- Checkpoint and resume support.
- Budget tracking for runs, failures, validation failures, and estimated cost.
- Retry policy for failed or invalid runs.
- Command risk classification to gate unsafe shell commands.
- Lightweight observability via JSONL event logs.
- PR helper for branch-aware handoff.

## Why this matters
Production guidance increasingly emphasizes durable execution, explicit error budgets, deterministic guardrails, and observability because most reliability issues arise in the harness rather than in the model alone.
