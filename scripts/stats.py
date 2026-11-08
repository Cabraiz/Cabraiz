"""Build the activity card and the "recently updated" list.

The public github-readme-stats and trophy services were returning 503 and 402
when this was written, so the card is generated here and served from this repo.

    GH_TOKEN=... python scripts/stats.py --out dist [--include-private]

Without a token that can read private repositories the card only covers public
work, and it says so.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import subprocess
from collections import Counter
from pathlib import Path

LOGIN = os.environ.get("GITHUB_REPOSITORY_OWNER", "Cabraiz")
README = Path(__file__).resolve().parents[1] / "README.md"
# Housekeeping repositories that say nothing about the work.
HIDDEN_REPOS = {"Cabraiz", "commits-2020", "cabraiz-privacidade"}
NOT_LANGUAGES = {"HTML", "CSS", "Makefile", "Dockerfile", "Shell", "PowerShell", "CMake", "TSQL"}

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false,
                 orderBy: {field: PUSHED_AT, direction: DESC}) {
      nodes { name url isPrivate pushedAt primaryLanguage { name color } }
    }
  }
}
"""

THEMES = {
    "dark": {"bg": "#0d1117", "border": "#30363d", "text": "#e6edf3", "muted": "#8b949e", "track": "#21262d"},
    "light": {"bg": "#ffffff", "border": "#d0d7de", "text": "#1f2328", "muted": "#59636e", "track": "#eaeef2"},
}
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"


def fetch() -> dict:
    result = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={QUERY}", "-F", f"login={LOGIN}"],
        check=True, capture_output=True, text=True, encoding="utf-8",
    )
    return json.loads(result.stdout)["data"]["user"]


def streaks(days: list[tuple[str, int]], today: dt.date) -> tuple[int, int]:
    """Return (current, longest). A quiet today doesn't break the current streak."""
    longest = run = 0
    for _, count in days:
        run = run + 1 if count else 0
        longest = max(longest, run)
    current = 0
    for date, count in reversed(days):
        if count:
            current += 1
        elif date != today.isoformat():
            break
    return current, longest


def summarise(user: dict, include_private: bool, today: dt.date) -> dict:
    calendar = user["contributionsCollection"]["contributionCalendar"]
    days = [
        (day["date"], day["contributionCount"])
        for week in calendar["weeks"] for day in week["contributionDays"]
        if day["date"] <= today.isoformat()
    ]
    current, longest = streaks(days, today)
    repos = [r for r in user["repositories"]["nodes"] if include_private or not r["isPrivate"]]
    cutoff = (today - dt.timedelta(days=730)).isoformat()
    languages: Counter = Counter()
    colors = {}
    for repo in repos:
        language = repo["primaryLanguage"]
        if repo["pushedAt"] >= cutoff and language and language["name"] not in NOT_LANGUAGES:
            languages[language["name"]] += 1
            colors[language["name"]] = language["color"] or "#8b949e"
    return {
        "total": calendar["totalContributions"],
        "active_days": sum(1 for _, count in days if count),
        "current": current,
        "longest": longest,
        "languages": [(name, count, colors[name]) for name, count in languages.most_common(6)],
        "scope": "repository" if include_private else "public repository",
        "recent": [r for r in repos if not r["isPrivate"] and r["name"] not in HIDDEN_REPOS][:4],
    }


def card(stats: dict, theme: str) -> str:
    t = THEMES[theme]
    metrics = [
        (f"{stats['total']:,}", "contributions, last 12 months"),
        (f"{stats['active_days']}", "active days"),
        (f"{stats['longest']} days", "longest streak"),
        (f"{stats['current']} days", "current streak"),
    ]
    width, height = 840, 232
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'role="img" aria-label="GitHub activity summary and most used languages">',
        f'<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="10" fill="{t["bg"]}" stroke="{t["border"]}"/>',
        f'<g font-family="{FONT}">',
    ]
    for i, (value, label) in enumerate(metrics):
        x, y = 32 + (i % 2) * 190, 74 + (i // 2) * 88
        parts.append(f'<text x="{x}" y="{y}" font-size="30" font-weight="600" fill="{t["text"]}">{html.escape(value)}</text>')
        parts.append(f'<text x="{x}" y="{y + 24}" font-size="13" fill="{t["muted"]}">{html.escape(label)}</text>')
    parts.append(f'<line x1="430" y1="28" x2="430" y2="{height - 28}" stroke="{t["border"]}"/>')
    parts.append(
        f'<text x="462" y="46" font-size="13" fill="{t["muted"]}">'
        f'Main language per {stats["scope"]}, last 24 months</text>'
    )
    top = max((count for _, count, _ in stats["languages"]), default=1)
    for i, (name, count, color) in enumerate(stats["languages"]):
        y = 76 + i * 26
        bar = max(6, round(190 * count / top))
        parts.append(f'<text x="462" y="{y}" font-size="13" fill="{t["text"]}">{html.escape(name)}</text>')
        parts.append(f'<rect x="570" y="{y - 10}" width="190" height="10" rx="5" fill="{t["track"]}"/>')
        parts.append(f'<rect x="570" y="{y - 10}" width="{bar}" height="10" rx="5" fill="{html.escape(color)}"/>')
        parts.append(f'<text x="772" y="{y}" font-size="13" fill="{t["muted"]}">{count}</text>')
    parts.append("</g></svg>")
    return "\n".join(parts)


def recent_markdown(stats: dict) -> str:
    links = " · ".join(f"[{repo['name']}]({repo['url']})" for repo in stats["recent"])
    return f"**Recently updated:** {links}"


def update_readme(markdown: str) -> None:
    text = README.read_text("utf-8")
    start, end = "<!-- recent:start -->", "<!-- recent:end -->"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if not pattern.search(text):
        raise ValueError("README is missing the recent markers")
    README.write_text(pattern.sub(lambda _: f"{start}\n{markdown}\n{end}", text, count=1), "utf-8", newline="\n")


def crop_3d(svg: str, crop: int = 70) -> str:
    """Drop the 3D chart's bottom row (total, stars, forks); the card covers the total."""
    match = re.search(r'<svg\b[^>]*?viewBox="0 0 (\d+) (\d+)"[^>]*>', svg)
    if not match:
        return svg
    width, height = int(match.group(1)), int(match.group(2))
    tag = match.group(0).replace(f'viewBox="0 0 {width} {height}"', f'viewBox="0 0 {width} {height - crop}"')
    tag = re.sub(r'\bheight="\d+"', f'height="{height - crop}"', tag, count=1)
    return svg.replace(match.group(0), tag, 1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="dist")
    parser.add_argument("--include-private", action="store_true")
    parser.add_argument("--crop-3d", nargs=2, action="append", default=[], metavar=("SRC", "DEST"))
    args = parser.parse_args()
    for source, destination in args.crop_3d:
        Path(destination).write_text(crop_3d(Path(source).read_text("utf-8")), "utf-8", newline="\n")
    stats = summarise(fetch(), args.include_private, dt.datetime.now(dt.timezone.utc).date())
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        (out / f"activity-{theme}.svg").write_text(card(stats, theme), "utf-8", newline="\n")
    update_readme(recent_markdown(stats))


if __name__ == "__main__":
    main()
