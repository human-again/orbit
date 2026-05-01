# Phase 5 Notes

This phase closes several remaining gaps from Phase 4.

## Added capabilities
- Central command runner with enforced risk gating middleware.
- Resume manager that identifies the next task from checkpoint or backlog state.
- Diff-aware evaluation based on git diff stats.
- Context compaction utilities for large tool outputs.
- Stack templates for Python, Node, and monorepos.

## Why this matters
Recent harness guidance emphasizes middleware-based command control, structured resume workflows, diff-aware review, and context shaping so the harness can scale safely over long coding sessions.
