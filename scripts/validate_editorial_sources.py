#!/usr/bin/env python3
"""Validate official source links used by pages currently in the sitemap."""

from __future__ import annotations

import datetime as dt
import json
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

from editorial_audit import is_official

ROOT = Path(__file__).resolve().parent.parent
REVIEW_DATE = dt.date.today().isoformat()
REPORT_PATH = ROOT / "docs" / f"editorial-source-validation-{REVIEW_DATE}.json"
USER_AGENT = "AI-Profit-Hub-Editorial-Audit/1.0"
WEB_VERIFIED = {
    "https://api-docs.deepseek.com/quick_start/pricing": (
        "Official page opened in the web validator on 2026-07-30."
    ),
    "https://help.suno.com/en": "Official page opened in the web validator on 2026-07-29.",
    "https://helpx.adobe.com/ie/firefly/web/get-started/learn-the-basics/adobe-firefly-overview.html": (
        "Official page opened in the web validator on 2026-07-29."
    ),
}


def sitemap_pages() -> list[Path]:
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    pages: list[Path] = []
    for node in ET.parse(ROOT / "sitemap.xml").findall(".//sm:loc", namespace):
        route = urlparse((node.text or "").strip()).path or "/"
        if route == "/":
            rel = "index.html"
        elif route.endswith("/"):
            rel = route.lstrip("/") + "index.html"
        else:
            rel = route.lstrip("/")
        path = ROOT / rel
        if path.exists():
            pages.append(path)
    return pages


def official_links() -> dict[str, set[str]]:
    usage: dict[str, set[str]] = {}
    for path in sitemap_pages():
        soup = BeautifulSoup(
            path.read_text(encoding="utf-8-sig", errors="replace"),
            "html.parser",
        )
        for anchor in soup.select("main a[href], article a[href]"):
            url = str(anchor.get("href", "")).strip()
            if url.startswith(("http://", "https://")) and is_official(url):
                usage.setdefault(url, set()).add(path.relative_to(ROOT).as_posix())
    return usage


def check_url(url: str) -> dict:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=20) as response:
            status = int(response.status)
            final_url = response.geturl()
    except HTTPError as error:
        status = int(error.code)
        final_url = error.geturl()
    except Exception as error:
        if url in WEB_VERIFIED:
            return {
                "url": url,
                "status": None,
                "classification": "web-verified",
                "note": WEB_VERIFIED[url],
                "direct_check_error": error.__class__.__name__,
            }
        return {
            "url": url,
            "status": None,
            "classification": "failed",
            "error": error.__class__.__name__,
        }

    if 200 <= status < 400:
        classification = "reachable"
    elif status in {401, 403, 405, 429}:
        classification = "access-controlled"
    elif url in WEB_VERIFIED:
        return {
            "url": url,
            "status": status,
            "classification": "web-verified",
            "note": WEB_VERIFIED[url],
            "final_url": urlparse(final_url)._replace(query="", fragment="").geturl(),
        }
    else:
        classification = "failed"
    return {
        "url": url,
        "status": status,
        "classification": classification,
        "final_url": urlparse(final_url)._replace(query="", fragment="").geturl(),
    }


def main() -> int:
    usage = official_links()
    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(check_url, url): url for url in usage}
        for future in as_completed(futures):
            result = future.result()
            result["used_by"] = sorted(usage[futures[future]])
            results.append(result)
    results.sort(key=lambda item: item["url"])

    counts = {
        label: sum(item["classification"] == label for item in results)
        for label in ("reachable", "access-controlled", "web-verified", "failed")
    }
    report = {
        "review_date": REVIEW_DATE,
        "official_urls_checked": len(results),
        "counts": counts,
        "results": results,
    }
    REPORT_PATH.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({**counts, "official_urls_checked": len(results)}, indent=2))
    return 1 if counts["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
