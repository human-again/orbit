from app.auth import authenticate, issue_session_label


USERS = [
    {"email": "orbit@example.com", "password": "launch-123"},
    {"email": "pilot@example.com", "password": "booster-456"},
]


def test_authenticate_accepts_case_insensitive_email() -> None:
    assert authenticate(USERS, "ORBIT@EXAMPLE.COM", "launch-123") is True


def test_authenticate_ignores_surrounding_whitespace() -> None:
    assert authenticate(USERS, "  pilot@example.com  ", "booster-456") is True


def test_issue_session_label_uses_canonical_email() -> None:
    assert issue_session_label(USERS, " Orbit@Example.com ", "launch-123") == "session:orbit@example.com"
