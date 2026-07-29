#!/usr/bin/env python3
"""Non-destructive editorial inventory and quality audit."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = "https://ai-profit-hub.com"
DECISIONS_PATH = ROOT / "data" / "editorial-decisions.json"
INVENTORY_PATH = ROOT / "docs" / "editorial-content-inventory-2026-07-29.json"
REPORT_PATH = ROOT / "docs" / "editorial-audit-current-2026-07-29.json"
SOCIAL_DOMAINS = {
    "facebook.com",
    "linkedin.com",
    "twitter.com",
    "x.com",
    "wa.me",
}
OFFICIAL_DOMAINS = {
    "adobe.com",
    "ai.google.dev",
    "anthropic.com",
    "api-docs.deepseek.com",
    "apple.com",
    "blackforestlabs.ai",
    "blogs.microsoft.com",
    "cursor.com",
    "deepseek.com",
    "developers.google.com",
    "developers.openai.com",
    "docs.anthropic.com",
    "docs.cursor.com",
    "docs.github.com",
    "docs.midjourney.com",
    "github.com",
    "google.com",
    "huggingface.co",
    "klingai.com",
    "ltxstudio.com",
    "microsoft.com",
    "notion.so",
    "notion.com",
    "ollama.com",
    "openai.com",
    "perplexity.ai",
    "qwenlm.github.io",
    "suno.com",
    "udio.com",
    "windsurf.com",
    "x.ai",
}
SPECULATIVE_RE = re.compile(
    r"\b(?:expected|expectation|future release|launching soon|likely to|"
    r"may launch|might launch|predicted|prediction|rumou?red|upcoming)\b",
    re.IGNORECASE,
)
ARABIC_RE = re.compile(
    "[\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff\ufb50-\ufdff\ufe70-\ufefc]"
)


@dataclass(frozen=True)
class Finding:
    severity: str
    category: str
    message: str


def tracked_html() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z", "*.html"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    return [
        ROOT / value.decode("utf-8", errors="surrogateescape")
        for value in result.stdout.split(b"\0")
        if value
    ]


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


def content_type(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel.endswith("/index.html"):
        return "hub"
    if rel.startswith("reviews/"):
        return "review"
    if rel.startswith("compare/"):
        return "comparison"
    if rel.startswith("guides/") or "guide" in path.stem:
        return "guide"
    if rel.startswith("companies/"):
        return "company"
    if rel.startswith("best-ai-tools/") or rel == "ai-tools-directory.html":
        return "tool-directory"
    if rel.startswith("articles/"):
        title = path.stem.lower()
        if "-vs-" in title or "comparison" in title:
            return "comparison"
        if "review" in title:
            return "review"
        return "article"
    if rel.startswith(("categories/", "business/", "coding/", "developers/", "news/",
                       "productivity/", "students/", "tutorials/")):
        return "hub"
    return "page"


def search_intent(kind: str, title: str) -> str:
    lowered = title.lower()
    if kind == "comparison" or " vs " in lowered:
        return "comparison decision"
    if kind == "review":
        return "product evaluation"
    if kind == "guide" or lowered.startswith("how to"):
        return "task completion"
    if kind in {"company", "hub"}:
        return "topic research"
    if kind == "tool-directory":
        return "tool discovery"
    if any(term in lowered for term in ("launch", "announces", "raises", "lawsuit")):
        return "news"
    return "informational"


def meta_content(soup: BeautifulSoup, key: str) -> str:
    node = soup.find("meta", attrs={"name": key}) or soup.find(
        "meta", attrs={"property": key}
    )
    return str(node.get("content", "")).strip() if node else ""


def external_links(soup: BeautifulSoup) -> list[str]:
    links: list[str] = []
    for node in soup.select("a[href]"):
        href = str(node.get("href", "")).strip()
        parsed = urlparse(href)
        host = parsed.netloc.lower().removeprefix("www.")
        if parsed.scheme not in {"http", "https"}:
            continue
        if host == "ai-profit-hub.com" or any(
            host == social or host.endswith("." + social) for social in SOCIAL_DOMAINS
        ):
            continue
        if href not in links:
            links.append(href)
    return links


def is_official(url: str) -> bool:
    host = urlparse(url).netloc.lower().removeprefix("www.")
    return any(host == domain or host.endswith("." + domain) for domain in OFFICIAL_DOMAINS)


def paragraph_too_long(soup: BeautifulSoup) -> bool:
    return any(len(node.get_text(" ", strip=True).split()) > 140 for node in soup.find_all("p"))


def has_heading_jump(soup: BeautifulSoup) -> bool:
    previous = 0
    for node in soup.find_all(re.compile(r"^h[1-6]$")):
        if node.find_parent(["footer", "header", "nav", "aside"]):
            continue
        current = int(node.name[1])
        if previous and current > previous + 1:
            return True
        previous = current
    return False


def page_findings(
    *,
    indexed: bool,
    kind: str,
    title: str,
    description: str,
    soup: BeautifulSoup,
    sources: list[str],
    words: int,
    text: str,
) -> list[Finding]:
    findings: list[Finding] = []
    if not indexed:
        return findings
    content = soup.find("main") or soup
    if not title:
        findings.append(Finding("technical_error", "missing_title", "Missing title"))
    elif len(title) < 20 or len(title) > 90:
        findings.append(
            Finding("editorial_warning", "title_quality", f"Title length is {len(title)}")
        )
    if not description:
        findings.append(
            Finding("technical_error", "missing_description", "Missing meta description")
        )
    elif len(description) < 90 or len(description) > 200:
        findings.append(
            Finding(
                "editorial_warning",
                "description_quality",
                f"Description length is {len(description)}",
            )
        )
    h1_count = len(soup.find_all("h1"))
    if h1_count != 1:
        findings.append(
            Finding("technical_error", "h1_structure", f"Expected one H1, found {h1_count}")
        )
    if has_heading_jump(content):
        findings.append(
            Finding("editorial_warning", "heading_hierarchy", "Heading levels are skipped")
        )
    if paragraph_too_long(content):
        findings.append(
            Finding("editorial_warning", "paragraph_length", "Contains a paragraph over 140 words")
        )
    minimum_words = {
        "article": 500,
        "review": 500,
        "comparison": 500,
        "guide": 500,
        "company": 300,
        "tool-directory": 350,
    }
    substantial = kind in minimum_words
    if substantial and words < minimum_words[kind]:
        findings.append(
            Finding("editorial_warning", "thin_content", f"Only {words} visible words")
        )
    if substantial and not sources:
        findings.append(
            Finding("editorial_warning", "missing_sources", "No non-social external source")
        )
    if substantial and len(sources) < 2 and not any(is_official(url) for url in sources):
        findings.append(
            Finding("editorial_warning", "missing_official_source", "No official source")
        )
    if SPECULATIVE_RE.search(text) and not sources:
        findings.append(
            Finding(
                "editorial_warning",
                "unsupported_future_language",
                "Future-looking language appears without a source",
            )
        )
    if kind == "review" and not re.search(
        r"documentation-based|hands-on|testing method|review methodology", text, re.I
    ):
        findings.append(
            Finding("editorial_warning", "missing_review_method", "Review method is not disclosed")
        )
    if kind == "comparison" and not content.find("table"):
        findings.append(
            Finding("editorial_warning", "missing_comparison_table", "Comparison has no table")
        )
    if substantial and "Hussein Harby" not in text:
        findings.append(
            Finding("editorial_warning", "missing_author", "Named author is not visible")
        )
    if ARABIC_RE.search(text):
        findings.append(
            Finding("technical_error", "language_policy", "Arabic script appears in page content")
        )
    return findings


def load_decisions() -> dict:
    return json.loads(DECISIONS_PATH.read_text(encoding="utf-8"))


def build_inventory() -> tuple[list[dict], dict]:
    routes = sitemap_routes()
    decisions = load_decisions()
    translated = set(decisions["translated_pages"])
    keep_articles = set(decisions["keep_articles"])
    noindex_pages = set(decisions.get("noindex_pages", []))
    redirect_paths = set(decisions.get("redirects", {}))
    inventory: list[dict] = []
    finding_counts: Counter[str] = Counter()
    severity_counts: Counter[str] = Counter()

    for path in tracked_html():
        rel = path.relative_to(ROOT).as_posix()
        if rel in {"article-template.html", "reviews/review-template.html"}:
            continue
        raw = path.read_text(encoding="utf-8-sig", errors="replace")
        soup = BeautifulSoup(raw, "html.parser")
        if soup.find("meta", attrs={"http-equiv": re.compile("^refresh$", re.I)}):
            action = "Redirect"
            indexed = False
            status = "redirect"
        else:
            robots = meta_content(soup, "robots").lower()
            indexed = route_for(path) in routes and "noindex" not in robots
            status = "indexed" if indexed else ("noindex" if "noindex" in robots else "unlisted")
            if rel in redirect_paths:
                action = "Redirect"
            elif rel in noindex_pages:
                action = "Noindex"
            elif rel.startswith("articles/") and rel not in keep_articles:
                action = "Archive"
            elif indexed:
                action = "Improve"
            else:
                action = "Noindex"

        title = soup.title.get_text(" ", strip=True) if soup.title else ""
        description = meta_content(soup, "description")
        text = soup.get_text(" ", strip=True)
        sources = external_links(soup)
        official_sources = [url for url in sources if is_official(url)]
        links = [str(node.get("href", "")).strip() for node in soup.select("a[href]")]
        kind = content_type(path)
        words = len(text.split())
        findings = page_findings(
            indexed=indexed,
            kind=kind,
            title=title,
            description=description,
            soup=soup,
            sources=sources,
            words=words,
            text=text,
        )
        for finding in findings:
            finding_counts[finding.category] += 1
            severity_counts[finding.severity] += 1
        dates = [
            value
            for value in (
                meta_content(soup, "article:published_time"),
                meta_content(soup, "article:modified_time"),
                meta_content(soup, "date"),
            )
            if value
        ]
        inventory.append(
            {
                "file_path": rel,
                "public_url": BASE_URL + route_for(path),
                "content_type": kind,
                "main_topic": re.sub(r"\s*\|\s*AI Profit Hub\s*$", "", title),
                "primary_search_intent": search_intent(kind, title),
                "index_status": status,
                "title": title,
                "meta_description": description,
                "word_count": words,
                "heading_count": {
                    "h1": len(soup.find_all("h1")),
                    "h2": len(soup.find_all("h2")),
                    "h3": len(soup.find_all("h3")),
                },
                "source_count": len(sources),
                "official_source_count": len(official_sources),
                "internal_link_count": sum(
                    1
                    for href in links
                    if href.startswith(("/", "../", "./"))
                    or (href.endswith(".html") and not href.startswith(("http://", "https://")))
                ),
                "external_link_count": len(sources),
                "last_updated_date": dates[-1] if dates else "",
                "author": meta_content(soup, "author")
                or ("Hussein Harby" if "Hussein Harby" in text else ""),
                "was_translated": rel in translated,
                "contains_speculative_claims": bool(SPECULATIVE_RE.search(text)),
                "contains_original_analysis": "Hussein's Take" in text,
                "contains_husseins_take": "Hussein's Take" in text,
                "appears_thin": words < (
                    {
                        "article": 500,
                        "review": 500,
                        "comparison": 500,
                        "guide": 500,
                        "company": 300,
                        "tool-directory": 350,
                    }.get(kind, 250)
                ),
                "overlaps_another_page": False,
                "recommended_action": action,
                "findings": [asdict(finding) for finding in findings],
            }
        )

    summary = {
        "pages_reviewed": len(inventory),
        "indexed_pages": sum(item["index_status"] == "indexed" for item in inventory),
        "translated_pages_reviewed": sum(item["was_translated"] for item in inventory),
        "recommended_actions": dict(Counter(item["recommended_action"] for item in inventory)),
        "findings_by_severity": dict(severity_counts),
        "findings_by_category": dict(finding_counts),
        "total_findings": sum(finding_counts.values()),
    }
    return inventory, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-reports", action="store_true")
    args = parser.parse_args()
    inventory, summary = build_inventory()
    if args.write_reports:
        INVENTORY_PATH.write_text(
            json.dumps(inventory, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        REPORT_PATH.write_text(
            json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(summary, indent=2))
    return 1 if summary["findings_by_severity"].get("technical_error", 0) else 0


if __name__ == "__main__":
    raise SystemExit(main())
