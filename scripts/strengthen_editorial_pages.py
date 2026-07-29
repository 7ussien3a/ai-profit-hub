#!/usr/bin/env python3
"""Strengthen sources, authorship, metadata, and review transparency."""

from __future__ import annotations

import html
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
REVIEW_DATE = "July 29, 2026"

SOURCES: dict[str, list[tuple[str, str]]] = {
    "articles/build-agentic-workflow-2026.html": [
        ("OpenAI, A Practical Guide to Building Agents", "https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf"),
        ("Anthropic documentation, tool use", "https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview"),
    ],
    "articles/cursor-ai-review-2026-update.html": [
        ("Cursor official pricing documentation", "https://docs.cursor.com/account/pricing"),
        ("Cursor official model documentation", "https://docs.cursor.com/models"),
    ],
    "articles/cursor-vs-windsurf-gpt-5-6-sol-2026.html": [
        ("Cursor official documentation", "https://docs.cursor.com/"),
        ("Windsurf official documentation", "https://docs.windsurf.com/"),
        ("OpenAI GPT-5.6 model documentation", "https://developers.openai.com/api/docs/models/gpt-5.6-sol"),
    ],
    "articles/deepseek-r1-vs-qwen.html": [
        ("DeepSeek transparency center", "https://www.deepseek.com/en/transparency/"),
        ("Qwen official project site", "https://qwenlm.github.io/"),
    ],
    "articles/deepseek-v4-china-ai-model-2026.html": [
        ("DeepSeek V4 official release", "https://api-docs.deepseek.com/news/news260424/"),
        ("DeepSeek official models and pricing", "https://api-docs.deepseek.com/quick_start/pricing"),
        ("DeepSeek transparency center", "https://www.deepseek.com/en/transparency/"),
    ],
    "articles/free-alternatives-midjourney.html": [
        ("Midjourney official documentation", "https://docs.midjourney.com/"),
        ("Black Forest Labs official site", "https://blackforestlabs.ai/"),
        ("Adobe Firefly official product page", "https://www.adobe.com/products/firefly.html"),
    ],
    "articles/gpt-5-6-sol-review-2026.html": [
        ("OpenAI GPT-5.6 Sol model documentation", "https://developers.openai.com/api/docs/models/gpt-5.6-sol"),
        ("OpenAI model comparison", "https://developers.openai.com/api/docs/models/compare"),
        ("OpenAI model guidance", "https://developers.openai.com/api/docs/guides/latest-model"),
    ],
    "articles/gpt-5-6-vs-claude-5-comparison-2026.html": [
        ("OpenAI GPT-5.6 Sol documentation", "https://developers.openai.com/api/docs/models/gpt-5.6-sol"),
        ("Anthropic Claude Sonnet 5 announcement", "https://www.anthropic.com/news/claude-sonnet-5"),
    ],
    "articles/notion-ai-organization.html": [
        ("Notion AI official product page", "https://www.notion.com/product/ai"),
        ("Notion Help Center, Notion AI", "https://www.notion.com/help/guides/category/ai"),
    ],
    "companies/anthropic.html": [
        ("Anthropic official site", "https://www.anthropic.com/"),
        ("Anthropic Claude documentation", "https://docs.anthropic.com/en/docs/about-claude/models/overview"),
    ],
    "companies/deepseek.html": [
        ("DeepSeek transparency center", "https://www.deepseek.com/en/transparency/"),
        ("DeepSeek API change log", "https://api-docs.deepseek.com/updates/"),
        ("DeepSeek official pricing", "https://api-docs.deepseek.com/quick_start/pricing"),
    ],
    "companies/google.html": [
        ("Google Gemini model documentation", "https://ai.google.dev/gemini-api/docs/models"),
        ("Google AI official site", "https://ai.google/"),
    ],
    "companies/microsoft.html": [
        ("Microsoft AI official site", "https://www.microsoft.com/en-us/ai"),
        ("Microsoft Build 2026 official announcement", "https://blogs.microsoft.com/blog/2026/06/02/microsoft-build-2026-be-yourself-at-work/"),
    ],
    "companies/openai.html": [
        ("OpenAI official model catalog", "https://developers.openai.com/api/docs/models"),
        ("OpenAI research and announcements", "https://openai.com/news/"),
    ],
    "companies/perplexity.html": [
        ("Perplexity official site", "https://www.perplexity.ai/"),
        ("Perplexity Help Center", "https://www.perplexity.ai/help-center"),
    ],
    "compare/chatgpt-vs-claude.html": [
        ("OpenAI ChatGPT pricing", "https://openai.com/chatgpt/pricing/"),
        ("Anthropic Claude pricing", "https://www.anthropic.com/pricing"),
    ],
    "compare/chatgpt-vs-gemini.html": [
        ("OpenAI ChatGPT pricing", "https://openai.com/chatgpt/pricing/"),
        ("Google Gemini model documentation", "https://ai.google.dev/gemini-api/docs/models"),
    ],
    "compare/claude-vs-gemini.html": [
        ("Anthropic Claude documentation", "https://docs.anthropic.com/en/docs/about-claude/models/overview"),
        ("Google Gemini model documentation", "https://ai.google.dev/gemini-api/docs/models"),
    ],
    "compare/deepseek-r1-vs-meituan-longcat-2.html": [
        ("DeepSeek transparency center", "https://www.deepseek.com/en/transparency/"),
        ("Meituan LongCat official GitHub organization", "https://github.com/meituan-longcat"),
    ],
    "compare/deepseek-r1-vs-qwen-max.html": [
        ("DeepSeek transparency center", "https://www.deepseek.com/en/transparency/"),
        ("Qwen official project site", "https://qwenlm.github.io/"),
    ],
    "compare/gemini-2-5-pro-vs-gpt-5-5.html": [
        ("Google Gemini model documentation", "https://ai.google.dev/gemini-api/docs/models"),
        ("OpenAI model catalog", "https://developers.openai.com/api/docs/models"),
    ],
    "compare/gemini-3-5-flash-vs-claude-fable-5.html": [
        ("Google Gemini 3.5 Flash documentation", "https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash"),
        ("Anthropic official announcements", "https://www.anthropic.com/news"),
    ],
    "compare/claude-sonnet-5-vs-gemini-3-5-flash.html": [
        ("Anthropic Claude Sonnet 5 announcement", "https://www.anthropic.com/news/claude-sonnet-5"),
        ("Google Gemini 3.5 Flash documentation", "https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash"),
    ],
    "compare/midjourney-v6-vs-flux-1.html": [
        ("Midjourney official documentation", "https://docs.midjourney.com/"),
        ("Black Forest Labs official site", "https://blackforestlabs.ai/"),
    ],
    "compare/midjourney-vs-dalle.html": [
        ("Midjourney official documentation", "https://docs.midjourney.com/"),
        ("OpenAI image generation guide", "https://developers.openai.com/api/docs/guides/image-generation"),
    ],
    "compare/perplexity-vs-chatgpt.html": [
        ("Perplexity Help Center", "https://www.perplexity.ai/help-center"),
        ("OpenAI ChatGPT pricing", "https://openai.com/chatgpt/pricing/"),
    ],
    "compare/suno-v4-vs-udio.html": [
        ("Suno official help center", "https://help.suno.com/"),
        ("Udio official help center", "https://help.udio.com/"),
    ],
    "reviews/chatgpt-review.html": [
        ("OpenAI ChatGPT pricing", "https://openai.com/chatgpt/pricing/"),
        ("OpenAI model catalog", "https://developers.openai.com/api/docs/models"),
    ],
    "reviews/claude-ai-review.html": [
        ("Anthropic Claude pricing", "https://www.anthropic.com/pricing"),
        ("Anthropic Claude documentation", "https://docs.anthropic.com/en/docs/about-claude/models/overview"),
    ],
    "reviews/perplexity-review.html": [
        ("Perplexity official site", "https://www.perplexity.ai/"),
        ("Perplexity Help Center", "https://www.perplexity.ai/help-center"),
    ],
}

TITLES = {
    "articles/build-agentic-workflow-2026.html": "Build an Agentic Workflow: Practical 2026 Guide | AI Profit Hub",
    "articles/cursor-ai-review-2026-update.html": "Cursor AI Review: Features, Pricing, Strengths and Limits | AI Profit Hub",
    "articles/cursor-vs-windsurf-gpt-5-6-sol-2026.html": "Cursor vs Windsurf: Coding Workflow Comparison | AI Profit Hub",
    "articles/deepseek-v4-china-ai-model-2026.html": "DeepSeek V4 Guide: Models, Access, Pricing and Limits | AI Profit Hub",
    "articles/free-alternatives-midjourney.html": "Free Midjourney Alternatives: Features and Trade-offs | AI Profit Hub",
    "articles/google-gemma-4-local-ai-laptop-2026.html": "Google Gemma 4 Guide: Local Models, Hardware and Limits | AI Profit Hub",
    "articles/google-notebooklm-ultimate-guide-2026.html": "Google NotebookLM Guide: Research, Sources and Audio | AI Profit Hub",
    "articles/gpt-5-6-sol-review-2026.html": "GPT-5.6 Sol Review: Features, Pricing and Limitations | AI Profit Hub",
    "articles/gpt-5-6-vs-claude-5-comparison-2026.html": "GPT-5.6 Sol vs Claude Sonnet 5: Practical Comparison | AI Profit Hub",
    "articles/kling-3-turbo-ltx-2-video-ai-2026.html": "Kling 3 Turbo vs LTX-2: Video AI Comparison | AI Profit Hub",
    "articles/microsoft-mai-7-models-copilot-2026.html": "Microsoft MAI Models: Build 2026 Guide | AI Profit Hub",
    "articles/openai-proposes-5-percent-government-stake-trump-20260703.html": "OpenAI Government Stake Proposal: What the Reports Say | AI Profit Hub",
    "articles/qwen-robot-tencent-hunyuan-agents-2026.html": "Qwen-Robot and Hunyuan Agents: 2026 Guide | AI Profit Hub",
    "articles/south-korea-518-billion-chipmaking-hub-samsung-sk-20260703.html": "South Korea Chip Hub: Samsung and SK Investment Explained | AI Profit Hub",
    "articles/verdent-freebuff-dyad-mirofish-coding-agents-2026.html": "Coding Agents Compared: Verdent, Freebuff, Dyad and Mirofish | AI Profit Hub",
    "compare/gemini-2-5-pro-vs-gpt-5-5.html": "Gemini 2.5 Pro vs GPT-5.5: Practical Comparison | AI Profit Hub",
    "compare/gemini-3-5-flash-vs-claude-fable-5.html": "Gemini 3.5 Flash vs Claude Fable 5 | AI Profit Hub",
    "compare/midjourney-v6-vs-flux-1.html": "Midjourney v6 vs Flux.1: Image Generator Comparison | AI Profit Hub",
    "guides/how-to-use-deepseek-v4-for-coding-2026.html": "How to Use DeepSeek V4 for Coding: 2026 Guide | AI Profit Hub",
    "reviews/claude-sonnet-5-review.html": "Claude Sonnet 5 Review: Features, Pricing and Limits | AI Profit Hub",
}

DESCRIPTIONS = {
    "articles/cursor-vs-windsurf-gpt-5-6-sol-2026.html": "Compare Cursor and Windsurf using documented features, pricing, privacy controls, model access, and practical coding workflows.",
    "articles/deepseek-v4-china-ai-model-2026.html": "A source-backed guide to DeepSeek V4 models, official access methods, current API pricing, capabilities, and practical limitations.",
    "articles/google-gemma-4-local-ai-laptop-2026.html": "Review Google Gemma 4 model options, local hardware requirements, supported workflows, deployment choices, and documented limitations.",
    "articles/gpt-5-6-sol-review-2026.html": "A documentation-based review of GPT-5.6 Sol covering model access, pricing, capabilities, limitations, and suitable professional use cases.",
    "articles/microsoft-mai-7-models-copilot-2026.html": "A source-backed guide to Microsoft's MAI model family announced at Build 2026, including access, intended uses, and availability limits.",
    "articles/south-korea-518-billion-chipmaking-hub-samsung-sk-20260703.html": "A sourced analysis of South Korea's semiconductor investment plans, the roles of Samsung and SK Hynix, and the execution risks involved.",
    "guides/how-to-use-deepseek-v4-for-coding-2026.html": "Set up DeepSeek V4 for coding with official API details, model selection guidance, practical prompts, cost controls, and security cautions.",
    "reviews/claude-sonnet-5-review.html": "A documentation-based Claude Sonnet 5 review covering official capabilities, introductory pricing, limitations, access, and best use cases.",
}

METHODOLOGY = {
    "articles/cursor-ai-review-2026-update.html": "This is a documentation-based review. We checked Cursor's official pricing, model, privacy, and workflow documentation on July 29, 2026. No hands-on benchmark is claimed.",
    "articles/gpt-5-6-sol-review-2026.html": "This is a documentation-based review of OpenAI's published model specifications, pricing, and guidance as checked on July 29, 2026. AI Profit Hub did not run an independent benchmark for this article.",
    "reviews/chatgpt-review.html": "This documentation-based review compares the public ChatGPT plans, official model documentation, stated product features, and common user workflows. No independent performance benchmark is claimed.",
    "reviews/claude-ai-review.html": "This documentation-based review examines Anthropic's official model and pricing documentation, product access, stated capabilities, and practical limitations. No independent benchmark is claimed.",
    "reviews/claude-sonnet-5-review.html": "This documentation-based review uses Anthropic's launch announcement, system card, and published pricing. It does not claim hands-on testing or an independent benchmark.",
    "reviews/perplexity-review.html": "This documentation-based review checks Perplexity's published product and help documentation, plan structure, source workflow, and limitations. No independent benchmark is claimed.",
}

COMPARISON_TABLES = {
    "articles/cursor-vs-windsurf-gpt-5-6-sol-2026.html": """
<section data-editorial-comparison>
  <h2>Documented comparison at a glance</h2>
  <div style="overflow-x:auto">
    <table>
      <thead><tr><th>Decision factor</th><th>Cursor</th><th>Windsurf</th></tr></thead>
      <tbody>
        <tr><td>Review basis</td><td>Official product and pricing documentation</td><td>Official product documentation</td></tr>
        <tr><td>Best evaluation method</td><td>Test against your repository and usage limits</td><td>Test against your repository and usage limits</td></tr>
        <tr><td>Pricing check</td><td>Confirm the current Cursor pricing page</td><td>Confirm the current Windsurf pricing page</td></tr>
        <tr><td>Privacy check</td><td>Review the current privacy-mode documentation</td><td>Review the current data and privacy documentation</td></tr>
      </tbody>
    </table>
  </div>
</section>
""",
    "articles/gpt-5-6-vs-claude-5-comparison-2026.html": """
<section data-editorial-comparison>
  <h2>Official model comparison</h2>
  <div style="overflow-x:auto">
    <table>
      <thead><tr><th>Published detail</th><th>GPT-5.6 Sol</th><th>Claude Sonnet 5</th></tr></thead>
      <tbody>
        <tr><td>Provider</td><td>OpenAI</td><td>Anthropic</td></tr>
        <tr><td>API model ID</td><td><code>gpt-5.6-sol</code></td><td><code>claude-sonnet-5</code></td></tr>
        <tr><td>Review basis</td><td>Official model documentation</td><td>Official launch announcement and system card</td></tr>
        <tr><td>Selection advice</td><td colspan="2">Run representative tasks with a fixed rubric; provider benchmarks are not interchangeable.</td></tr>
      </tbody>
    </table>
  </div>
</section>
""",
}


def sitemap_routes() -> set[str]:
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return {
        urlparse((node.text or "").strip()).path or "/"
        for node in ET.parse(ROOT / "sitemap.xml").findall(".//sm:loc", namespace)
    }


def route_for(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    return "/" + rel


def replace_meta(text: str, key: str, value: str) -> str:
    tag_re = re.compile(
        rf'<meta\b(?=[^>]*(?:name|property)=["\']{re.escape(key)}["\'])[^>]*>',
        re.IGNORECASE,
    )
    match = tag_re.search(text)
    if not match:
        return text
    tag = match.group(0)
    escaped = html.escape(value, quote=True)
    if re.search(r'\bcontent=["\'][^"\']*["\']', tag, re.IGNORECASE):
        updated = re.sub(
            r'\bcontent=(["\'])[^"\']*\1',
            f'content="{escaped}"',
            tag,
            count=1,
            flags=re.IGNORECASE,
        )
    else:
        updated = tag[:-1] + f' content="{escaped}">'
    return text[: match.start()] + updated + text[match.end() :]


def update_json_ld(text: str, title: str | None, description: str | None) -> str:
    pattern = re.compile(
        r'(<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)',
        re.IGNORECASE | re.DOTALL,
    )

    def replace(match: re.Match[str]) -> str:
        try:
            data = json.loads(match.group(2))
        except json.JSONDecodeError:
            return match.group(0)
        objects = data if isinstance(data, list) else [data]
        for item in objects:
            if not isinstance(item, dict):
                continue
            if title and "headline" in item:
                item["headline"] = re.sub(r"\s*\|\s*AI Profit Hub\s*$", "", title)
            if description and "description" in item:
                item["description"] = description
        return match.group(1) + "\n" + json.dumps(data, indent=2) + "\n" + match.group(3)

    return pattern.sub(replace, text)


def insert_before_main_end(text: str, block: str) -> str:
    if re.search(r"</main>", text, re.IGNORECASE):
        return re.sub(r"</main>", block + "\n</main>", text, count=1, flags=re.IGNORECASE)
    return re.sub(r"<footer\b", block + "\n<footer", text, count=1, flags=re.IGNORECASE)


def source_block(items: list[tuple[str, str]]) -> str:
    links = "\n".join(
        f'    <li><a href="{html.escape(url, quote=True)}" target="_blank" '
        f'rel="noopener noreferrer">{html.escape(label)}</a></li>'
        for label, url in items
    )
    return f"""
<section class="editorial-sources" data-editorial-sources>
  <h2>Primary sources and review basis</h2>
  <p>Product facts and availability were checked against the sources below on {REVIEW_DATE}. Provider benchmarks and product claims are attributed to their publishers and are not presented as independent AI Profit Hub test results.</p>
  <ul>
{links}
  </ul>
</section>
"""


def add_byline(text: str, relative_author: str) -> str:
    if "Editorial review by Hussein Harby" in text or "Hussein Harby" in BeautifulSoup(text, "html.parser").get_text(" ", strip=True):
        return text
    note = (
        f'<p class="editorial-byline" data-editorial-byline>'
        f'Editorial review by <a href="{relative_author}">Hussein Harby</a>. '
        f'Reviewed {REVIEW_DATE}. Unless explicitly stated otherwise, this page is '
        f'documentation-based and does not claim hands-on testing.</p>'
    )
    return re.sub(r"(</h1>)", r"\1\n" + note, text, count=1, flags=re.IGNORECASE)


def main() -> int:
    indexed = sitemap_routes()
    changed = 0
    sources_added = 0
    bylines_added = 0
    methods_added = 0
    tables_added = 0
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in {"node_modules", ".git"} for part in path.parts):
            continue
        rel = path.relative_to(ROOT).as_posix()
        if route_for(path) not in indexed:
            continue
        text = path.read_text(encoding="utf-8-sig")
        original = text
        title = TITLES.get(rel)
        description = DESCRIPTIONS.get(rel)
        if title:
            text = re.sub(
                r"<title>.*?</title>",
                f"<title>{html.escape(title)}</title>",
                text,
                count=1,
                flags=re.IGNORECASE | re.DOTALL,
            )
            for key in ("og:title", "twitter:title"):
                text = replace_meta(text, key, title)
        if description:
            for key in ("description", "og:description", "twitter:description"):
                text = replace_meta(text, key, description)
        if title or description:
            text = update_json_ld(text, title, description)
        if rel in SOURCES and "data-editorial-sources" not in text:
            text = insert_before_main_end(text, source_block(SOURCES[rel]))
            sources_added += 1
        if rel in METHODOLOGY and "data-review-methodology" not in text:
            block = (
                '<section class="review-methodology" data-review-methodology>'
                '<h2>Review methodology</h2><p>'
                + html.escape(METHODOLOGY[rel])
                + "</p></section>"
            )
            text = insert_before_main_end(text, block)
            methods_added += 1
        if rel in COMPARISON_TABLES and "data-editorial-comparison" not in text:
            text = insert_before_main_end(text, COMPARISON_TABLES[rel])
            tables_added += 1
        kind = ""
        if rel.startswith("articles/"):
            kind = "article"
        elif rel.startswith("reviews/"):
            kind = "review"
        elif rel.startswith("compare/") and not rel.endswith("/index.html"):
            kind = "comparison"
        elif rel.startswith("companies/"):
            kind = "company"
        elif rel.startswith("best-ai-tools/") and not rel.endswith("/index.html"):
            kind = "tool"
        elif rel == "ai-tools-directory.html":
            kind = "tool"
        if kind:
            before = text
            depth = len(Path(rel).parts) - 1
            author_path = "../" * depth + "author/hussein-harby.html"
            text = add_byline(text, author_path)
            if text != before:
                bylines_added += 1
        if text != original:
            path.write_text(text, encoding="utf-8", newline="")
            changed += 1
    print(
        json.dumps(
            {
                "files_updated": changed,
                "source_sections_added": sources_added,
                "bylines_added": bylines_added,
                "methodology_sections_added": methods_added,
                "comparison_tables_added": tables_added,
                "titles_improved": len(TITLES),
                "descriptions_improved": len(DESCRIPTIONS),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
