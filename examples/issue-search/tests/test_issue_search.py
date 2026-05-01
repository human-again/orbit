from app.dashboard import filter_issues, render_dashboard


def test_filter_issues_matches_titles_case_insensitively() -> None:
    filtered = filter_issues("login")

    assert [issue["id"] for issue in filtered] == [101]


def test_render_dashboard_preserves_query_value() -> None:
    html = render_dashboard("retry")

    assert 'value="retry"' in html
    assert "Search results collapse after retry" in html
    assert "Billing export needs CSV header" not in html


def test_render_dashboard_shows_empty_state_when_nothing_matches() -> None:
    html = render_dashboard("missing")

    assert "No issues matched that search." in html
