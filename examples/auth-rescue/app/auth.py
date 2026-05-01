from __future__ import annotations


def _normalize_email(email: str) -> str:
    return email.strip().casefold()


def find_user_by_email(users: list[dict[str, str]], email: str) -> dict[str, str] | None:
    normalized = _normalize_email(email)
    for user in users:
        if _normalize_email(user["email"]) == normalized:
            return user
    return None


def authenticate(users: list[dict[str, str]], email: str, password: str) -> bool:
    user = find_user_by_email(users, email)
    return bool(user and user["password"] == password)


def issue_session_label(users: list[dict[str, str]], email: str, password: str) -> str | None:
    user = find_user_by_email(users, email)
    if not user or user["password"] != password:
        return None
    return f"session:{_normalize_email(user['email'])}"
