# Mission: Auth Service

## Objective
Implement a secure authentication module with token issuance, validation, and refresh — proven by tests.

## In scope
- Login, logout, token refresh endpoints or functions
- Password hashing (bcrypt or argon2 — never plaintext)
- Token validation middleware or decorator
- Tests for each auth flow

## Out of scope
- OAuth / social login
- User profile management
- Email verification flows

## Definition of done
- All auth flow tests pass
- Passwords are never stored or logged in plaintext
- Expired and tampered tokens are rejected
- The backlog task is marked `done` with `passes: true`
