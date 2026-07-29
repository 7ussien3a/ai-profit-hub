#!/usr/bin/env python3
"""Replace the legacy stock-author portrait with a local abstract editorial mark."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STOCK_URL_RE = re.compile(
    r"https://images\.unsplash\.com/photo-1507003211169-0a1dd7228f2d"
    r"[^\"'\s)<]*"
)
LOCAL_ABSOLUTE = "https://ai-profit-hub.com/images/tech_abstract_design.webp"


def relative_image(path: Path) -> str:
    depth = len(path.relative_to(ROOT).parts) - 1
    return "../" * depth + "images/tech_abstract_design.webp"


def update_html(path: Path, text: str) -> str:
    local = relative_image(path)
    updated = re.sub(
        r'(\bsrc\s*=\s*["\'])'
        + STOCK_URL_RE.pattern
        + r'(["\'])',
        lambda match: match.group(1) + local + match.group(2),
        text,
        flags=re.IGNORECASE,
    )
    updated = STOCK_URL_RE.sub(LOCAL_ABSOLUTE, updated)
    updated = re.sub(
        r"(?:(?:\.\./)*)images/author-hussein\.jpg",
        local,
        updated,
        flags=re.IGNORECASE,
    )
    for old_alt in (
        "Hussein - Founder of AI Profit Hub",
        "Hussein - AI Profit Hub Editor",
        "Hussein Harby",
        "Hussein",
    ):
        updated = updated.replace(
            f'alt="{old_alt}"',
            'alt="AI Profit Hub editorial mark"',
        )
    return updated


def main() -> int:
    files_updated = 0
    references_replaced = 0
    for path in [*ROOT.rglob("*.html"), *ROOT.rglob("*.js")]:
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        before = len(STOCK_URL_RE.findall(text)) + text.lower().count(
            "author-hussein.jpg"
        )
        if not before:
            continue
        updated = (
            update_html(path, text)
            if path.suffix.lower() == ".html"
            else STOCK_URL_RE.sub("/images/tech_abstract_design.webp", text)
        )
        if updated != text:
            path.write_text(updated, encoding="utf-8", newline="")
            files_updated += 1
            references_replaced += before

    print(
        json.dumps(
            {
                "files_updated": files_updated,
                "stock_author_references_replaced": references_replaced,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
