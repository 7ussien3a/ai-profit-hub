#!/usr/bin/env python3
"""Remove indexed-page links to noindex content and update redirect sources."""

from __future__ import annotations

import html
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = "https://ai-profit-hub.com"
DECISIONS_PATH = ROOT / "data" / "editorial-decisions.json"
ANCHOR_RE = re.compile(
    r"<a\b(?P<attributes>[^>]*)>(?P<body>.*?)</a>",
    re.IGNORECASE | re.DOTALL,
)
HREF_RE = re.compile(
    r"\bhref\s*=\s*(?P<quote>[\"'])(?P<href>.*?)(?P=quote)",
    re.IGNORECASE | re.DOTALL,
)


def route_for(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    return "/" + rel


def path_for_route(route: str) -> Path:
    if route == "/":
        return ROOT / "index.html"
    rel = route.lstrip("/")
    if route.endswith("/"):
        rel += "index.html"
    return ROOT / rel


def sitemap_routes() -> list[str]:
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return [
        urlparse((node.text or "").strip()).path or "/"
        for node in ET.parse(ROOT / "sitemap.xml").findall(".//sm:loc", namespace)
    ]


def noindex_routes() -> set[str]:
    routes: set[str] = set()
    for path in ROOT.rglob("*.html"):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        soup = BeautifulSoup(text, "html.parser")
        robots = soup.find("meta", attrs={"name": re.compile("^robots$", re.I)})
        if robots and "noindex" in str(robots.get("content", "")).lower():
            routes.add(route_for(path))
    return routes


def main() -> int:
    decisions = json.loads(DECISIONS_PATH.read_text(encoding="utf-8"))
    redirects = {
        "/" + source.lstrip("/"): destination
        for source, destination in decisions.get("redirects", {}).items()
    }
    blocked = noindex_routes()
    updated_links = 0
    unwrapped_links = 0
    changed_files = 0

    for route in sitemap_routes():
        path = path_for_route(route)
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8-sig")
        page_url = BASE_URL + route

        def replace_anchor(match: re.Match[str]) -> str:
            nonlocal updated_links, unwrapped_links
            attributes = match.group("attributes")
            href_match = HREF_RE.search(attributes)
            if not href_match:
                return match.group(0)
            href = html.unescape(href_match.group("href")).strip()
            target = urlparse(urljoin(page_url, href)).path or "/"
            if target in redirects:
                destination = redirects[target]
                replacement = (
                    f'href={href_match.group("quote")}{destination}'
                    f'{href_match.group("quote")}'
                )
                new_attributes = (
                    attributes[: href_match.start()]
                    + replacement
                    + attributes[href_match.end() :]
                )
                updated_links += 1
                return f"<a{new_attributes}>{match.group('body')}</a>"
            if target in blocked:
                unwrapped_links += 1
                return match.group("body")
            return match.group(0)

        updated = ANCHOR_RE.sub(replace_anchor, text)
        if updated != text:
            path.write_text(updated, encoding="utf-8", newline="")
            changed_files += 1

    print(
        json.dumps(
            {
                "files_updated": changed_files,
                "redirect_links_updated": updated_links,
                "archived_links_unwrapped": unwrapped_links,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
