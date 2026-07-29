#!/usr/bin/env python3
"""Remove corrupted emoji placeholders from indexable production pages."""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
PLACEHOLDER_RE = re.compile(r"\?{2,}")
OPERATOR_RE = re.compile(r"[\w)\]]\s+\?\?\s+[\w(\[]")


def route_for(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    return "/" + rel


def sitemap_routes() -> set[str]:
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return {
        urlparse((node.text or "").strip()).path or "/"
        for node in ET.parse(ROOT / "sitemap.xml").findall(".//sm:loc", namespace)
    }


def main() -> int:
    indexed = sitemap_routes()
    changed = 0
    replacements = 0
    for path in sorted(ROOT.rglob("*.html")):
        if route_for(path) not in indexed:
            continue
        text = path.read_text(encoding="utf-8-sig")
        text = text.replace("Built with ?? for the AI community", "Built for the AI community")
        suspicious = OPERATOR_RE.findall(text)
        if suspicious:
            raise RuntimeError(
                f"Refusing to replace possible operators in {path.relative_to(ROOT)}: "
                f"{suspicious[:3]}"
            )
        count = len(PLACEHOLDER_RE.findall(text))
        if not count:
            continue
        updated = PLACEHOLDER_RE.sub("", text)
        path.write_text(updated, encoding="utf-8", newline="")
        changed += 1
        replacements += count
    print(json.dumps({"files_updated": changed, "placeholders_removed": replacements}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
