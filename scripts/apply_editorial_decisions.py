#!/usr/bin/env python3
"""Apply reviewed editorial status decisions without deleting public pages."""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DECISIONS_PATH = ROOT / "data" / "editorial-decisions.json"
ROBOTS_TAG = '  <meta name="robots" content="noindex, follow">\n'
STATUS_TAG = (
    '  <meta name="editorial-status" '
    'content="Archived pending source and originality review">\n'
)
CARD_RE = re.compile(
    r"\s*<article\b[^>]*class=[\"'][^\"']*\barticle-card\b[^\"']*[\"'][^>]*>"
    r".*?</article>",
    re.IGNORECASE | re.DOTALL,
)


def route_for(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    return "/" + rel


def normalize_route(value: str) -> str:
    parsed = urlparse(value)
    if parsed.netloc and parsed.netloc != "ai-profit-hub.com":
        return ""
    route = parsed.path
    if not route.startswith("/"):
        route = "/" + route.lstrip("./")
    return route


def set_noindex(path: Path) -> bool:
    text = path.read_text(encoding="utf-8-sig")
    if re.search(r'<meta\b[^>]*http-equiv=["\']refresh["\']', text, re.IGNORECASE):
        return False
    original = text
    robots_re = re.compile(
        r'<meta\b(?=[^>]*name=["\']robots["\'])[^>]*>',
        re.IGNORECASE,
    )
    if robots_re.search(text):
        text = robots_re.sub(ROBOTS_TAG.strip(), text, count=1)
    else:
        text = re.sub(r"</head>", ROBOTS_TAG + "</head>", text, count=1, flags=re.IGNORECASE)
    if 'name="editorial-status"' not in text:
        text = re.sub(r"</head>", STATUS_TAG + "</head>", text, count=1, flags=re.IGNORECASE)
    if text != original:
        path.write_text(text, encoding="utf-8", newline="")
        return True
    return False


def update_redirects(redirects: dict[str, str]) -> int:
    path = ROOT / "vercel.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    existing = {entry["source"]: entry for entry in data.get("redirects", [])}
    added = 0
    for rel, destination in redirects.items():
        source = "/" + rel.removesuffix(".html") + ".html"
        entry = {
            "source": source,
            "destination": destination,
            "permanent": True,
        }
        if existing.get(source) != entry:
            existing[source] = entry
            added += 1
    data["redirects"] = sorted(existing.values(), key=lambda item: item["source"])
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return added


def prune_homepage(archived_routes: set[str]) -> int:
    path = ROOT / "index.html"
    text = path.read_text(encoding="utf-8")
    removed = 0

    def replace_card(match: re.Match[str]) -> str:
        nonlocal removed
        card = match.group(0)
        hrefs = re.findall(r'href=["\']([^"\']+)["\']', card, re.IGNORECASE)
        if any(normalize_route(href) in archived_routes for href in hrefs):
            removed += 1
            return ""
        return card

    updated = CARD_RE.sub(replace_card, text)
    if updated != text:
        path.write_text(updated, encoding="utf-8", newline="")
    return removed


def main() -> int:
    decisions = json.loads(DECISIONS_PATH.read_text(encoding="utf-8"))
    keep = set(decisions["keep_articles"])
    redirects = decisions.get("redirects", {})
    changed = 0
    archived_routes: set[str] = set()
    for path in sorted((ROOT / "articles").glob("*.html")):
        rel = path.relative_to(ROOT).as_posix()
        if rel in keep:
            continue
        archived_routes.add(route_for(path))
        changed += int(set_noindex(path))
    for value in decisions.get("noindex_pages", []):
        path = ROOT / value
        if path.exists():
            archived_routes.add(route_for(path))
            changed += int(set_noindex(path))
    added_redirects = update_redirects(redirects)
    removed_cards = prune_homepage(archived_routes)
    print(
        json.dumps(
            {
                "archived_article_routes": len(archived_routes),
                "files_updated": changed,
                "redirects_added_or_updated": added_redirects,
                "homepage_cards_removed": removed_cards,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
