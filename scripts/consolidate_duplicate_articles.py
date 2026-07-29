#!/usr/bin/env python3
"""Consolidate duplicate legacy articles and maintain direct permanent redirects."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = "https://ai-profit-hub.com"
GROUPS = {
    "articles/6g-networks-and-ai-samsung-lg-vision.html": [
        "articles/article79.html",
        "articles/article80.html",
    ],
    "articles/adobe-agentic-ai-creative-workflows.html": [
        "articles/article81.html",
        "articles/article82.html",
    ],
    "articles/ai-adoption-headcount-growth-ramp-study-2026.html": [
        "articles/article85.html",
    ],
    "articles/ai-cost-per-task-economy-2026.html": [
        "articles/article86.html",
    ],
    "articles/ai-digital-marketing-trends-2026.html": [
        "articles/article87.html",
    ],
    "articles/ai-ethics-challenges-guide.html": [
        "articles/article88.html",
    ],
    "articles/ai-impact-on-jobs-2026.html": [
        "articles/article89.html",
    ],
    "articles/ai-in-art-therapy.html": [
        "articles/article90.html",
    ],
    "articles/ai-in-everyday-life-algorithms.html": [
        "articles/article91.html",
    ],
    "articles/ai-medical-skin-patch-wearable-doctor.html": [
        "articles/article92.html",
    ],
    "articles/ai-seo-optimization-guide-2026.html": [
        "articles/article93.html",
    ],
    "articles/ai-work-automation-guide-2026.html": [
        "articles/article97.html",
    ],
    "articles/anthropic-surpasses-openai-in-revenue-as-google-prepares-agentic-gemini-3-5-pro.html": [
        "articles/article61.html",
    ],
    "articles/china-s-ai-leap-deepseek-s-7-4b-funding-and-huawei-s-ascend-950-series.html": [
        "articles/article75.html",
    ],
    "articles/what-is-agentic-coding-future.html": [
        "articles/article83.html",
    ],
}
META_TAG_RE = re.compile(
    r'<meta\b(?=[^>]*http-equiv=["\']refresh["\'])[^>]*>',
    re.IGNORECASE,
)
CONTENT_RE = re.compile(
    r'content=(?P<quote>["\'])(?P<value>.*?)(?P=quote)',
    re.IGNORECASE,
)


def public_path(relative_path: str) -> str:
    return "/" + relative_path.replace("\\", "/")


def refresh_target(text: str) -> str:
    tag = META_TAG_RE.search(text)
    if not tag:
        return ""
    content = CONTENT_RE.search(tag.group(0))
    if not content:
        return ""
    match = re.search(r"url\s*=\s*(.+)", content.group("value"), re.IGNORECASE)
    target = match.group(1).strip().strip("\"'") if match else ""
    if target.startswith(BASE_URL):
        return target.removeprefix(BASE_URL)
    return target


def word_count(text: str) -> int:
    visible = re.sub(r"<script.*?</script>|<style.*?</style>", " ", text, flags=re.I | re.S)
    visible = re.sub(r"<[^>]+>", " ", visible)
    return len(visible.split())


def rewrite_page_url(text: str, source: str, canonical: str) -> str:
    source_public = public_path(source)
    canonical_public = public_path(canonical)
    text = text.replace(f"{BASE_URL}{source_public}", f"{BASE_URL}{canonical_public}")
    text = text.replace(source_public, canonical_public)
    canonical_tag = (
        f'<link rel="canonical" href="{BASE_URL}{canonical_public}"/>'
    )
    text = re.sub(
        r'<link[^>]+rel=["\']canonical["\'][^>]*>',
        canonical_tag,
        text,
        count=1,
        flags=re.IGNORECASE,
    )
    return text


def redirect_page(destination: str) -> str:
    absolute = f"{BASE_URL}{destination}"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="robots" content="noindex, follow">
  <meta http-equiv="refresh" content="0; url={destination}">
  <link rel="canonical" href="{absolute}">
  <title>Redirecting | AI Profit Hub</title>
</head>
<body>
  <p>This article has moved. <a href="{destination}">Continue to the current version</a>.</p>
</body>
</html>
"""


def final_destination(source: str, redirects: dict[str, str]) -> str:
    current = redirects.get(source, source)
    seen = {source}
    while current in redirects and current not in seen:
        seen.add(current)
        current = redirects[current]
    return current


def main() -> int:
    vercel_path = ROOT / "vercel.json"
    vercel = json.loads(vercel_path.read_text(encoding="utf-8-sig"))
    redirects = {
        item["source"]: item["destination"]
        for item in vercel.get("redirects", [])
        if item.get("source") and item.get("destination")
    }

    for path in sorted((ROOT / "articles").glob("*.html")):
        text = path.read_text(encoding="utf-8")
        destination = refresh_target(text)
        if destination:
            redirects[public_path(path.relative_to(ROOT).as_posix())] = destination

    for canonical, aliases in GROUPS.items():
        candidates = [canonical, *aliases]
        source = max(
            candidates,
            key=lambda name: word_count((ROOT / name).read_text(encoding="utf-8")),
        )
        source_text = (ROOT / source).read_text(encoding="utf-8")
        canonical_text = rewrite_page_url(source_text, source, canonical)
        (ROOT / canonical).write_text(canonical_text, encoding="utf-8")

        destination = public_path(canonical)
        for alias in aliases:
            (ROOT / alias).write_text(redirect_page(destination), encoding="utf-8")
            redirects[public_path(alias)] = destination
        print(f"Canonical: {canonical} (content source: {source})")

    direct = {
        source: final_destination(destination, redirects)
        for source, destination in redirects.items()
    }
    direct["/index.html"] = "/"
    vercel["redirects"] = [
        {"source": source, "destination": destination, "permanent": True}
        for source, destination in sorted(direct.items())
        if source != destination
    ]
    vercel_path.write_text(json.dumps(vercel, indent=2) + "\n", encoding="utf-8")
    print(f"Permanent redirects: {len(vercel['redirects'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
