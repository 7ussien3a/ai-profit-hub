#!/usr/bin/env python3
"""Align production canonical URLs and matching metadata with static routes."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = "https://ai-profit-hub.com"
NON_PRODUCTION = {
    "article-template.html",
    "reviews/review-template.html",
}
CANONICAL_RE = re.compile(
    r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\'][^>]*>'
    r'|<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']canonical["\'][^>]*>',
    re.IGNORECASE,
)
REFRESH_RE = re.compile(
    r'<meta\b(?=[^>]*http-equiv=["\']refresh["\'])[^>]*>',
    re.IGNORECASE,
)


def tracked_html() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "*.html"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return [ROOT / line for line in result.stdout.splitlines() if line.strip()]


def expected_url(path: Path) -> str:
    relative = path.relative_to(ROOT).as_posix()
    if relative == "index.html":
        public_path = "/"
    elif relative.endswith("/index.html"):
        public_path = "/" + relative.removesuffix("index.html")
    else:
        public_path = "/" + relative
    return BASE_URL + public_path


def main() -> int:
    changed = 0
    for path in tracked_html():
        if not path.exists():
            continue
        if path.relative_to(ROOT).as_posix() in NON_PRODUCTION:
            continue
        text = path.read_text(encoding="utf-8")
        if REFRESH_RE.search(text):
            continue
        match = CANONICAL_RE.search(text)
        if not match:
            continue
        canonical = next(value for value in match.groups() if value)
        expected = expected_url(path)
        if canonical == expected:
            continue
        updated = text.replace(canonical, expected)
        path.write_text(updated, encoding="utf-8")
        changed += 1
        print(f"Canonical: {path.relative_to(ROOT).as_posix()} -> {expected}")
    print(f"Repaired canonical metadata in {changed} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
