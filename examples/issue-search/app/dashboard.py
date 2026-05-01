from __future__ import annotations

from html import escape

ISSUES = [
    {"id": 101, "title": "Login redirect flashes on refresh", "status": "open", "updated": "2026-04-26"},
    {"id": 102, "title": "Search results collapse after retry", "status": "open", "updated": "2026-04-27"},
    {"id": 103, "title": "Billing export needs CSV header", "status": "closed", "updated": "2026-04-25"},
    {"id": 104, "title": "Invite email copy needs review", "status": "open", "updated": "2026-04-28"},
]


def filter_issues(query: str) -> list[dict[str, str | int]]:
    normalized = query.strip().casefold()
    if not normalized:
        return list(ISSUES)
    return [issue for issue in ISSUES if normalized in issue["title"].casefold()]


def render_dashboard(query: str) -> str:
    safe_query = escape(query)
    cards = "\n".join(
        (
            '<li class="issue-card" data-status="{status}">'
            '<span class="issue-id">#{id}</span>'
            '<span class="issue-title">{title}</span>'
            '<span class="issue-updated">{updated}</span>'
            "</li>"
        ).format(
            id=issue["id"],
            title=escape(str(issue["title"])),
            status=escape(str(issue["status"])),
            updated=escape(str(issue["updated"])),
        )
        for issue in filter_issues(query)
    )
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Issue Search Demo</title>
    <style>
      body {{ font-family: Helvetica, Arial, sans-serif; margin: 2rem; background: #f6f3eb; color: #1b1b1b; }}
      main {{ max-width: 760px; margin: 0 auto; background: #fffdf8; padding: 2rem; border: 1px solid #d5c8b4; }}
      form {{ display: flex; gap: 0.75rem; margin-bottom: 1rem; }}
      input {{ flex: 1; padding: 0.75rem; border: 1px solid #bfae93; }}
      button {{ padding: 0.75rem 1rem; border: 0; background: #194c43; color: white; }}
      .issue-list {{ list-style: none; padding: 0; margin: 0; display: grid; gap: 0.75rem; }}
      .issue-card {{ display: grid; gap: 0.25rem; padding: 1rem; border: 1px solid #e0d5c5; background: #fff; }}
      .issue-id {{ font-size: 0.85rem; color: #6a645d; }}
      .empty {{ padding: 1rem; border: 1px dashed #bfae93; }}
    </style>
  </head>
  <body>
    <main>
      <p>Visible proof demo: add scoped search without changing the rest of the dashboard.</p>
      <form method="get">
        <input type="search" name="q" value="{safe_query}" placeholder="Search issues by title">
        <button type="submit">Search</button>
      </form>
      {"<p class='empty'>No issues matched that search.</p>" if not cards else f"<ul class='issue-list'>{cards}</ul>"}
    </main>
  </body>
</html>
"""
