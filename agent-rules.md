# Agent Rules

## Execution rules
- Work on only one task per iteration.
- Prefer the smallest coherent change.
- Stop and report if requirements are ambiguous.
- Do not modify secrets, infra, or database schemas without approval.
- Do not redefine acceptance criteria.

## Research rules
- Use research only when the task requires external knowledge.
- Keep research bounded by explicit questions.
- Write findings to `research/<task-id>.md` using the template.

## Validation rules
- Run required validation commands before marking complete.
- If validation fails, either fix it in-scope or mark blocked.
- Never claim success without recorded evidence.

## Escalation rules
Escalate when:
- The task conflicts with mission or scope.
- A destructive migration is required.
- The same failure repeats twice.
- Tooling is unavailable or permissions are insufficient.
