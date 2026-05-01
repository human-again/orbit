# Research Brief

## Task
- ID: task-003
- Title: Add bounded research handoff

## Questions
- What should a bounded research artifact contain?
- How should findings be passed to the coding worker?
- What stop conditions should prevent research sprawl?

## Findings
- Research artifacts should capture the exact question, distilled findings, sources, risks, and a recommended implementation path.
- A coding worker should receive a short synthesized summary, not raw search output.
- Research should be constrained by a fixed question list, explicit output schema, and a limited budget.

## Sources
- Anthropic engineering notes on multi-agent research and long-running harnesses.

## Risks
- Over-research can consume budget without improving implementation quality.
- Raw findings can overload the coding worker and increase drift.

## Recommendation
- Keep research optional, bounded, and written to a task-specific markdown file.
