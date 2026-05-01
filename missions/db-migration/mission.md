# Mission: Database Migration

## Objective
Add a new table or column to the schema with a safe, zero-downtime, reversible migration.

## In scope
- Migration script with `up` and `down` paths
- ORM model or schema update to match
- Tests verifying the schema change and model behaviour

## Out of scope
- Backfilling existing rows (open a separate mission once the schema is live)
- Changing indexes on large tables without an explicit plan
- Renaming columns on tables with live traffic (requires a multi-step approach)

## Definition of done
- Migration runs forward (`up`) without errors
- Migration rolls back (`down`) cleanly, restoring previous state
- ORM model tests pass after the change
- The backlog task is marked `done` with `passes: true`
