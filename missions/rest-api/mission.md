# Mission: REST API Service

## Objective
Build a well-tested REST API service with standard CRUD endpoints, request validation, and structured error responses.

## In scope
- Route definitions and handler functions
- Request validation and structured 4xx error responses
- Unit tests for each endpoint (happy path + error paths)

## Out of scope
- Authentication (handle in a separate mission using `auth-service/`)
- Database migrations (handle in a separate mission using `db-migration/`)
- Deployment configuration

## Definition of done
- All endpoint tests pass
- 4xx errors return structured JSON: `{"error": "...", "message": "..."}`
- No unhandled exceptions on valid or invalid input
- The backlog task is marked `done` with `passes: true`
