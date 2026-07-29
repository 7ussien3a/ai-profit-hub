#!/usr/bin/env python3
"""Repair known legacy links and preserve obsolete public routes with redirects."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPLACEMENTS = {
    "/articles/ai-smartphones-future.html": "/articles/ai-in-everyday-life-algorithms.html",
    "articles/japan-s-sovereign-physical-ai-softbank-leads-6-16b-noetra-consortium.html": "/articles/japan-s-sovereign-physical-ai-softbank-leads-6-16b-noetra-consortium.html",
    "articles/south-korea-s-500b-ai-supercycle-samsung-hbm4-and-sk-hynix-factory-boom.html": "/articles/south-korea-s-500b-ai-supercycle-samsung-hbm4-and-sk-hynix-factory-expansion.html",
    "/articles/openai.html": "/companies/openai.html",
    "/articles/openai-guide.html": "/companies/openai.html",
    "/articles/anthropic-guide.html": "/companies/anthropic.html",
    "/articles/best-ai-seo-tools.html": "/articles/ai-seo-optimization-guide-2026.html",
    "/articles/openai-developments.html": "/companies/openai.html",
    "/articles/ai-tools-directory.html": "/ai-tools-directory.html",
    "/articles/chatgpt-vs-claude-3.html": "/compare/chatgpt-vs-claude.html",
    "/articles/llm-latest-updates.html": "/articles/ai-updates-timeline-2026.html",
    "/articles/article1.html": "/articles/south-korea-s-500b-ai-supercycle-samsung-hbm4-and-sk-hynix-factory-expansion.html",
    "/articles/article30.html": "/articles/ai-stock-market-analysis-beginners-guide.html",
    "/ai-tools/": "/ai-tools-directory.html",
    "/articles/index.html": "/news/",
    "/ai/": "/ai-glossary.html",
    "/categories/design": "/categories/ai-video.html",
    "articles/grok-3-vs-gpt-5-6-openai-xai-2026.html": "/articles/grok-3-vs-gpt-5-6-openai-xai-2026.html",
    "articles/ai-model-distillation-war-2026.html": "/articles/ai-model-distillation-war-2026.html",
    "articles/ai-seo-optimization-guide-2026.html": "/articles/ai-seo-optimization-guide-2026.html",
    "../articles/": "/news/",
    "articles/cursor-ai-review-2026-update.html": "/articles/cursor-ai-review-2026-update.html",
    "/articles/best-ai-business-tools.html": "/articles/best-ai-agents-business-automation.html",
    "/articles/ai-updates-hub.html": "/articles/ai-updates-timeline-2026.html",
    "/articles/gemini-vs-claude-fable-1782528977487.html": "/compare/gemini-3-5-flash-vs-claude-fable-5.html",
    "/terms": "/terms-of-service.html",
}
URL_ATTRIBUTE_RE = re.compile(
    r'(?P<prefix>\b(?:href|src)=["\'])(?P<url>[^"\']+)(?P<suffix>["\'])',
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


def public_source(value: str) -> str:
    if value.startswith("/"):
        return value
    while value.startswith("../"):
        value = value[3:]
    return "/" + value


def resolve(destination: str, redirects: dict[str, str]) -> str:
    seen: set[str] = set()
    current = destination
    while current in redirects and current not in seen:
        seen.add(current)
        current = redirects[current]
    return current


def repair_url_attributes(text: str) -> tuple[str, int]:
    count = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal count
        url = match.group("url")
        repaired = url.replace(
            "terms-of-service.html-of-service.html",
            "terms-of-service.html",
        )
        if repaired.startswith("//articles/"):
            repaired = repaired[1:]
        if repaired != url:
            url = repaired
            count += 1
        if url.startswith("/news/") and url.endswith(".html"):
            candidate = ROOT / "articles" / url.removeprefix("/news/")
            if candidate.exists():
                url = "/articles/" + candidate.name
                count += 1
        destination = REPLACEMENTS.get(url)
        if destination:
            url = destination
            count += 1
        return f'{match.group("prefix")}{url}{match.group("suffix")}'

    return URL_ATTRIBUTE_RE.sub(replace, text), count


def main() -> int:
    changed_files = 0
    replacements = 0
    for path in tracked_html():
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        updated, count = repair_url_attributes(text)
        replacements += count
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed_files += 1

    vercel_path = ROOT / "vercel.json"
    vercel = json.loads(vercel_path.read_text(encoding="utf-8-sig"))
    redirects = {
        item["source"]: item["destination"]
        for item in vercel.get("redirects", [])
        if item.get("source") and item.get("destination")
    }
    for source, destination in REPLACEMENTS.items():
        route = public_source(source)
        if route != destination and not (ROOT / route.lstrip("/")).exists():
            redirects[route] = destination
    direct = {
        source: resolve(destination, redirects)
        for source, destination in redirects.items()
    }
    vercel["redirects"] = [
        {"source": source, "destination": destination, "permanent": True}
        for source, destination in sorted(direct.items())
        if source != destination
    ]
    vercel_path.write_text(json.dumps(vercel, indent=2) + "\n", encoding="utf-8")

    print(f"Repaired {replacements} links across {changed_files} files")
    print(f"Permanent redirects: {len(vercel['redirects'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
