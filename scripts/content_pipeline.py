#!/usr/bin/env python3
"""AI Profit Hub content pipeline for the Obsidian Markdown workspace."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import subprocess
import sys
import textwrap
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from html.parser import HTMLParser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
DATA = ROOT / "data"
BASE_URL = "https://ai-profit-hub.com"
ALLOWED_STATUS = {"draft", "review", "scheduled", "published", "archived", "noindex"}
ALLOWED_TYPES = {
    "article",
    "news",
    "review",
    "comparison",
    "guide",
    "tool",
    "company",
    "model",
    "prompt",
}
EDITORIAL_ONLY_FOLDERS = {"dashboards", "reports", "research", "sources"}
RSS_TYPES = {"article", "news", "review", "comparison", "guide"}
TYPE_DIR = {
    "article": "articles",
    "news": "articles",
    "review": "reviews",
    "comparison": "compare",
    "guide": "guides",
    "tool": "ai-tools-directory",
    "company": "companies",
    "model": "articles",
    "prompt": "prompts-library",
}
REQUIRED = {
    "title",
    "slug",
    "description",
    "contentType",
    "category",
    "author",
    "status",
    "updatedAt",
    "featuredImage",
    "imageAlt",
    "language",
}
PUBLISHED_REQUIRED = REQUIRED | {"publishedAt", "canonical"}
ARABIC_SCRIPT_RE = re.compile(r"[\u0600-\u06ff]")
UNSAFE_HTML_RE = re.compile(
    r"<\s*(?:script|iframe|object|embed|form)\b|"
    r"\bon[a-z]+\s*=|javascript\s*:",
    re.I,
)


@dataclass
class ContentItem:
    path: Path
    meta: dict[str, Any]
    body: str
    html_body: str = ""
    reading_time: int = 1
    public_path: str = ""
    public_url: str = ""
    body_text: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def slug(self) -> str:
        return str(self.meta.get("slug", "")).strip()

    @property
    def title(self) -> str:
        return str(self.meta.get("title", "")).strip()

    @property
    def status(self) -> str:
        return str(self.meta.get("status", "")).strip().lower()

    @property
    def content_type(self) -> str:
        return str(self.meta.get("contentType", "")).strip().lower()

    @property
    def is_published(self) -> bool:
        return self.status == "published" and not bool(self.meta.get("draft", False))


def warn(message: str) -> None:
    print(f"WARNING: {message}")


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "":
        return ""
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value in {"null", "None"}:
        return None
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(part.strip()) for part in split_csv(inner)]
    return value


def split_csv(value: str) -> list[str]:
    parts: list[str] = []
    current = []
    quote = ""
    for char in value:
        if char in {"'", '"'}:
            quote = "" if quote == char else char if not quote else quote
        if char == "," and not quote:
            parts.append("".join(current))
            current = []
        else:
            current.append(char)
    parts.append("".join(current))
    return parts


def parse_frontmatter(text: str, path: Path) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        raise ValueError(f"{path}: missing frontmatter block")
    end = text.find("\n---", 3)
    if end == -1:
        raise ValueError(f"{path}: frontmatter block is not closed")
    raw = text[3:end].strip("\n")
    body = text[end + 4 :].lstrip("\r\n")
    lines = raw.splitlines()
    meta: dict[str, Any] = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        i += 1
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"{path}: invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value:
            meta[key] = parse_scalar(value)
            continue
        block: list[Any] = []
        while i < len(lines) and (lines[i].startswith("  ") or lines[i].startswith("\t")):
            item_line = lines[i].strip()
            i += 1
            if not item_line:
                continue
            if item_line.startswith("- "):
                payload = item_line[2:].strip()
                if ":" in payload and not payload.startswith(("http://", "https://")):
                    k, v = payload.split(":", 1)
                    entry: dict[str, Any] = {k.strip(): parse_scalar(v.strip())}
                    while i < len(lines) and lines[i].startswith("    "):
                        sub = lines[i].strip()
                        i += 1
                        if ":" in sub:
                            sk, sv = sub.split(":", 1)
                            entry[sk.strip()] = parse_scalar(sv.strip())
                    block.append(entry)
                else:
                    block.append(parse_scalar(payload))
        meta[key] = block
    return meta, body


def load_content() -> list[ContentItem]:
    items: list[ContentItem] = []
    if not CONTENT.exists():
        return items
    for path in sorted(CONTENT.rglob("*.md")):
        relative = path.relative_to(CONTENT)
        if ".obsidian" in relative.parts:
            continue
        if "templates" in relative.parts:
            continue
        if EDITORIAL_ONLY_FOLDERS.intersection(relative.parts):
            continue
        if path.name.lower() in {"readme.md", "dashboard.md"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            item = ContentItem(path=path, meta={}, body="")
            item.errors.append(f"{path}: file is not valid UTF-8")
            items.append(item)
            continue
        try:
            meta, body = parse_frontmatter(text, path)
        except ValueError as exc:
            item = ContentItem(path=path, meta={}, body=text)
            item.errors.append(str(exc))
            items.append(item)
            continue
        item = ContentItem(path=path, meta=meta, body=body)
        item.reading_time = reading_time(body)
        assign_public_url(item)
        items.append(item)
    return items


def assign_public_url(item: ContentItem) -> None:
    slug = item.slug
    content_type = item.content_type
    if not slug or not content_type:
        return
    folder = TYPE_DIR.get(content_type, "articles")
    if folder.endswith(".html"):
        public_path = folder
    elif folder in {"ai-tools-directory", "prompts-library"}:
        public_path = f"articles/{slug}.html"
    else:
        public_path = f"{folder}/{slug}.html"
    item.public_path = public_path
    item.public_url = f"{BASE_URL}/{public_path}"


def reading_time(markdown: str) -> int:
    plain = re.sub(r"```.*?```", " ", markdown, flags=re.S)
    plain = re.sub(r"`[^`]+`", " ", plain)
    plain = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", plain)
    plain = re.sub(r"\[[^\]]+\]\([^)]+\)", " ", plain)
    words = re.findall(r"\b[\w'-]+\b", plain)
    return max(1, round(len(words) / 225))


def validate(items: list[ContentItem]) -> int:
    errors = 0
    title_map: dict[str, list[ContentItem]] = {}
    slug_map: dict[str, list[ContentItem]] = {}
    lookup = build_lookup(items)
    for item in items:
        rel = item.path.relative_to(ROOT)
        if item.errors:
            errors += len(item.errors)
            continue
        required = PUBLISHED_REQUIRED if item.status == "published" else REQUIRED
        for key in sorted(required):
            value = item.meta.get(key)
            if value is None or value == "" or value == []:
                add_issue(item, "errors" if item.status == "published" else "warnings", f"missing {key}")
        if item.status not in ALLOWED_STATUS:
            item.errors.append(f"invalid status: {item.status}")
        if item.content_type not in ALLOWED_TYPES:
            item.errors.append(f"unsupported contentType: {item.content_type}")
        if item.title and len(item.title) < 8:
            item.errors.append("title must contain at least 8 characters")
        description = str(item.meta.get("description") or "").strip()
        if description and len(description) < 60:
            item.errors.append("description must contain at least 60 characters")
        if item.meta.get("language") != "en":
            item.errors.append("language must be en")
        searchable_text = json.dumps(item.meta, ensure_ascii=False) + "\n" + item.body
        if ARABIC_SCRIPT_RE.search(searchable_text):
            item.errors.append("Arabic script is not allowed in tracked content")
        if UNSAFE_HTML_RE.search(item.body):
            add_issue(
                item,
                "errors" if item.status == "published" else "warnings",
                "unsafe HTML is not allowed",
            )
        if item.slug and not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", item.slug):
            item.errors.append("slug must be lowercase kebab-case")
        if item.status == "published" and bool(item.meta.get("draft", False)):
            item.errors.append("published content cannot set draft to true")
        for key in ("publishedAt", "updatedAt", "lastReviewed"):
            value = str(item.meta.get(key) or "").strip()
            if value and not parse_date(value):
                item.errors.append(f"invalid date in {key}: {value}")
        canonical = str(item.meta.get("canonical") or "").strip()
        if canonical:
            parsed = urlparse(canonical)
            if (
                parsed.scheme != "https"
                or parsed.netloc != "ai-profit-hub.com"
                or parsed.query
                or parsed.fragment
            ):
                item.errors.append("canonical must be a clean HTTPS URL on ai-profit-hub.com")
            elif item.public_url and canonical.rstrip("/") != item.public_url.rstrip("/"):
                item.errors.append(f"canonical must match generated URL: {item.public_url}")
        if item.is_published:
            if len(item.body.strip()) < 500:
                item.errors.append("published content body is too short")
            if not item.meta.get("sources") and item.content_type in {"news", "review", "comparison", "guide", "article", "model", "company"}:
                item.errors.append("published source-backed content requires sources")
        validate_sources(item)
        image = str(item.meta.get("featuredImage") or "")
        if image and not image_exists(image):
            item.errors.append(f"missing featured image: {image}")
        if image.startswith(("http://", "https://")):
            add_issue(
                item,
                "errors" if item.is_published else "warnings",
                "featured image must use a local project path",
            )
        if image and not str(item.meta.get("imageAlt") or "").strip():
            item.errors.append("featured image requires imageAlt")
        if image and 0 < len(str(item.meta.get("imageAlt") or "").strip()) < 10:
            item.errors.append("featured image alt text must contain at least 10 characters")
        broken_images = find_markdown_images(item.body)
        for alt, src in broken_images:
            if not alt.strip():
                item.errors.append(f"inline image missing alt text: {src}")
            if not image_exists(src):
                item.errors.append(f"missing inline image: {src}")
            if src.startswith(("http://", "https://")):
                add_issue(
                    item,
                    "errors" if item.is_published else "warnings",
                    f"inline image must use a local project path: {src}",
                )
        for target in find_wikilinks(item.body):
            matches = lookup.get(normalize_key(target), [])
            if not matches:
                item.errors.append(f"unresolved Wiki Link: {target}")
            elif len(matches) > 1:
                item.errors.append(f"ambiguous Wiki Link: {target}")
            elif item.is_published and not matches[0].is_published:
                item.errors.append(f"published Wiki Link target is not published: {target}")
        title_map.setdefault(normalize_key(item.title), []).append(item)
        slug_map.setdefault(item.slug, []).append(item)
        for issue in item.errors:
            print(f"ERROR: {rel}: {issue}")
        for issue in item.warnings:
            print(f"WARNING: {rel}: {issue}")
        errors += len(item.errors)
    for title, matches in title_map.items():
        if title and len(matches) > 1:
            names = ", ".join(str(m.path.relative_to(ROOT)) for m in matches)
            print(f"ERROR: duplicate title '{matches[0].title}': {names}")
            errors += 1
    for slug, matches in slug_map.items():
        if slug and len(matches) > 1:
            names = ", ".join(str(m.path.relative_to(ROOT)) for m in matches)
            print(f"ERROR: duplicate slug '{slug}': {names}")
            errors += 1
    if errors:
        fail(f"Content validation failed with {errors} error(s).")
        return 1
    print(f"Content validation passed for {len(items)} Markdown item(s).")
    return 0


def add_issue(item: ContentItem, attr: str, message: str) -> None:
    getattr(item, attr).append(message)


def validate_sources(item: ContentItem) -> None:
    sources = item.meta.get("sources") or []
    if not isinstance(sources, list):
        item.errors.append("sources must be a list")
        return
    for index, source in enumerate(sources, start=1):
        if isinstance(source, str):
            title = source
            url = source
        elif isinstance(source, dict):
            title = str(source.get("title") or "").strip()
            url = str(source.get("url") or "").strip()
        else:
            item.errors.append(f"source {index} must be a URL or title/url object")
            continue
        parsed = urlparse(url)
        if not title:
            item.errors.append(f"source {index} requires a title")
        if parsed.scheme != "https" or not parsed.netloc:
            add_issue(
                item,
                "errors" if item.is_published else "warnings",
                f"source {index} must use a valid HTTPS URL",
            )
        if parsed.netloc.casefold() == "example.com":
            add_issue(
                item,
                "errors" if item.is_published else "warnings",
                f"source {index} still uses a placeholder URL",
            )


def parse_date(value: str) -> dt.datetime | None:
    value = value.strip()
    if not value:
        return None
    try:
        normalized = value.replace("Z", "+00:00")
        return dt.datetime.fromisoformat(normalized)
    except ValueError:
        try:
            return dt.datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            return None


def image_exists(src: str) -> bool:
    src = src.strip()
    if not src:
        return False
    if src.startswith(("http://", "https://")):
        return True
    if src.startswith("/"):
        return (ROOT / src.lstrip("/")).exists()
    if src.startswith("content/"):
        return (ROOT / src).exists()
    return (CONTENT / src).exists() or (ROOT / src).exists()


def find_markdown_images(markdown: str) -> list[tuple[str, str]]:
    return re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", markdown)


def find_wikilinks(markdown: str) -> list[str]:
    return re.findall(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", markdown)


def build_lookup(items: list[ContentItem]) -> dict[str, list[ContentItem]]:
    lookup: dict[str, list[ContentItem]] = {}
    for item in items:
        for key in {item.title, item.slug, item.path.stem}:
            if key:
                lookup.setdefault(normalize_key(key), []).append(item)
    legacy_titles = collect_legacy_titles()
    for title, url in legacy_titles.items():
        pseudo = ContentItem(
            path=ROOT / url,
            meta={
                "title": title,
                "slug": Path(url).stem,
                "contentType": "article",
                "status": "published",
            },
            body="",
        )
        pseudo.public_path = url
        pseudo.public_url = f"{BASE_URL}/{url}"
        lookup.setdefault(normalize_key(title), []).append(pseudo)
        lookup.setdefault(normalize_key(Path(url).stem), []).append(pseudo)
    return lookup


def collect_legacy_titles() -> dict[str, str]:
    titles: dict[str, str] = {}
    for folder in ("articles", "reviews", "compare", "guides", "companies"):
        base = ROOT / folder
        if not base.exists():
            continue
        for path in base.glob("*.html"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            match = re.search(r"<title>(.*?)\s*\|\s*AI Profit Hub</title>", text, re.S)
            if match:
                rel = path.relative_to(ROOT).as_posix()
                titles[html.unescape(strip_tags(match.group(1)).strip())] = rel
    return titles


def normalize_key(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def build() -> int:
    items = load_content()
    if validate(items) != 0:
        return 1
    lookup = build_lookup(items)
    published = [item for item in items if item.is_published]
    manifest = load_manifest()
    previous_paths = set(manifest.values())
    remove_stale_pages(manifest, published)
    for item in published:
        item.html_body = render_markdown(item.body, lookup)
        item.body_text = strip_tags(item.html_body)
        write_page(item)
    write_manifest(published)
    update_sitemap(published, previous_paths)
    update_rss(published, previous_paths)
    search_entries = write_search_index(published)
    write_related_content(published, search_entries)
    print(f"Built {len(published)} published Markdown page(s).")
    return 0


def load_manifest() -> dict[str, str]:
    path = DATA / "content-manifest.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_manifest(items: list[ContentItem]) -> None:
    DATA.mkdir(exist_ok=True)
    data = {str(item.path.relative_to(ROOT).as_posix()): item.public_path for item in items}
    (DATA / "content-manifest.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def remove_stale_pages(old: dict[str, str], published: list[ContentItem]) -> None:
    keep = {item.public_path for item in published}
    for public_path in old.values():
        if public_path not in keep:
            target = ROOT / public_path
            if target.exists():
                target.unlink()


def render_markdown(markdown: str, lookup: dict[str, list[ContentItem]]) -> str:
    markdown = resolve_wikilinks(markdown, lookup)
    lines = markdown.splitlines()
    out: list[str] = []
    paragraph: list[str] = []
    in_code = False
    code_lang = ""
    code_lines: list[str] = []
    in_ul = False
    in_ol = False
    i = 0
    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip()
        if line.startswith("```"):
            if in_code:
                out.append(f'<pre><code class="language-{html.escape(code_lang)}">{html.escape(chr(10).join(code_lines))}</code></pre>')
                code_lines = []
                code_lang = ""
                in_code = False
            else:
                flush_paragraph(out, paragraph)
                in_code = True
                code_lang = line[3:].strip()
            i += 1
            continue
        if in_code:
            code_lines.append(raw)
            i += 1
            continue
        if not line.strip():
            flush_paragraph(out, paragraph)
            if in_ul:
                out.append("</ul>")
                in_ul = False
            if in_ol:
                out.append("</ol>")
                in_ol = False
            i += 1
            continue
        if line.startswith("|") and i + 1 < len(lines) and re.match(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?$", lines[i + 1].strip()):
            flush_paragraph(out, paragraph)
            rows = [line, lines[i + 1].strip()]
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i].strip())
                i += 1
            out.append(render_table(rows))
            continue
        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            flush_paragraph(out, paragraph)
            level = len(heading.group(1))
            text = heading.group(2).strip()
            out.append(f'<h{level} id="{slugify(strip_inline(text))}">{render_inline(text)}</h{level}>')
            i += 1
            continue
        if line.startswith("> [!"):
            flush_paragraph(out, paragraph)
            label = re.match(r"^> \[!([A-Z]+)\]\s*(.*)$", line)
            title = label.group(2).strip() if label else ""
            body: list[str] = []
            i += 1
            while i < len(lines) and lines[i].startswith(">"):
                body.append(lines[i].lstrip("> ").rstrip())
                i += 1
            out.append(f'<div class="content-callout"><strong>{html.escape(title or "Note")}</strong><p>{render_inline(" ".join(body))}</p></div>')
            continue
        if line.startswith(">"):
            flush_paragraph(out, paragraph)
            quote = line.lstrip("> ").strip()
            out.append(f"<blockquote>{render_inline(quote)}</blockquote>")
            i += 1
            continue
        if re.match(r"^\s*[-*]\s+", line):
            flush_paragraph(out, paragraph)
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{render_inline(re.sub(r'^\\s*[-*]\\s+', '', line))}</li>")
            i += 1
            continue
        if re.match(r"^\s*\d+\.\s+", line):
            flush_paragraph(out, paragraph)
            if not in_ol:
                out.append("<ol>")
                in_ol = True
            out.append(f"<li>{render_inline(re.sub(r'^\\s*\\d+\\.\\s+', '', line))}</li>")
            i += 1
            continue
        paragraph.append(line)
        i += 1
    flush_paragraph(out, paragraph)
    if in_ul:
        out.append("</ul>")
    if in_ol:
        out.append("</ol>")
    return "\n".join(out)


def flush_paragraph(out: list[str], paragraph: list[str]) -> None:
    if paragraph:
        out.append(f"<p>{render_inline(' '.join(paragraph))}</p>")
        paragraph.clear()


def render_table(rows: list[str]) -> str:
    header = split_table_row(rows[0])
    body_rows = [split_table_row(row) for row in rows[2:]]
    head = "".join(f"<th>{render_inline(cell)}</th>" for cell in header)
    body = "".join("<tr>" + "".join(f"<td>{render_inline(cell)}</td>" for cell in row) + "</tr>" for row in body_rows)
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def split_table_row(row: str) -> list[str]:
    row = row.strip().strip("|")
    return [cell.strip() for cell in row.split("|")]


def resolve_wikilinks(markdown: str, lookup: dict[str, list[ContentItem]]) -> str:
    def replace(match: re.Match[str]) -> str:
        target = match.group(1).strip()
        label = match.group(2).strip() if match.group(2) else target
        matches = lookup.get(normalize_key(target), [])
        if len(matches) == 1 and matches[0].public_path and matches[0].is_published:
            return f"[{label}](/{matches[0].public_path})"
        return label
    return re.sub(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", replace, markdown)


def render_inline(text: str) -> str:
    safe = html.escape(text)
    safe = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", render_image_match, safe)
    safe = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', safe)
    safe = re.sub(r"`([^`]+)`", r"<code>\1</code>", safe)
    safe = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", safe)
    safe = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", safe)
    return safe


def render_image_match(match: re.Match[str]) -> str:
    alt = match.group(1)
    src = match.group(2)
    return f'<img src="{src}" alt="{alt}" loading="lazy" width="900" height="500">'


def strip_inline(text: str) -> str:
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", text)
    return re.sub(r"[*_`]", "", text)


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return value or "section"


def strip_tags(value: str) -> str:
    return re.sub(r"<[^>]+>", " ", value).replace("\n", " ").strip()


def write_page(item: ContentItem) -> None:
    target = ROOT / item.public_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_page(item), encoding="utf-8")


def render_page(item: ContentItem) -> str:
    meta = item.meta
    title = str(meta["title"])
    desc = str(meta["description"])
    canonical = str(meta.get("canonical") or item.public_url)
    image = absolute_image(str(meta.get("featuredImage") or ""))
    image_src = public_image_path(str(meta.get("featuredImage") or ""))
    published = str(meta.get("publishedAt") or meta.get("updatedAt"))
    updated = str(meta.get("updatedAt") or published)
    schema_type = str(meta.get("schemaType") or schema_for(item.content_type))
    json_ld = {
        "@context": "https://schema.org",
        "@type": schema_type,
        "headline": title,
        "description": desc,
        "image": image,
        "author": {"@type": "Person", "name": str(meta.get("author")), "url": f"{BASE_URL}/author/hussein-harby.html"},
        "publisher": {"@type": "Organization", "name": "AI Profit Hub", "url": BASE_URL},
        "datePublished": published,
        "dateModified": updated,
        "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
    }
    faq_schema = extract_faq_schema(item.html_body)
    schema_blocks = [json.dumps(json_ld, ensure_ascii=False, indent=2)]
    if faq_schema:
        schema_blocks.append(json.dumps(faq_schema, ensure_ascii=False, indent=2))
    related = render_related(item)
    sources = render_sources(meta.get("sources") or [])
    disclosure = html.escape(str(meta.get("disclosure") or ""))
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)} | AI Profit Hub</title>
  <meta name="description" content="{html.escape(desc)}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{html.escape(canonical)}">
  <meta property="article:published_time" content="{html.escape(published)}">
  <meta property="article:modified_time" content="{html.escape(updated)}">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(desc)}">
  <meta property="og:image" content="{html.escape(image)}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{html.escape(canonical)}">
  <meta property="og:site_name" content="AI Profit Hub">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html.escape(title)}">
  <meta name="twitter:description" content="{html.escape(desc)}">
  <meta name="twitter:image" content="{html.escape(image)}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../css/style.css">
  <link rel="stylesheet" href="../css/article.css">
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-8CSEDW0FVR"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-8CSEDW0FVR');
  </script>
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4602905173099480" crossorigin="anonymous"></script>
  {"".join(f'<script type="application/ld+json">\\n{block}\\n  </script>\\n  ' for block in schema_blocks)}
</head>
<body>
  <header class="header">
    <nav class="nav-container">
      <a href="../index.html" class="logo"><span class="logo-icon">AI</span><span>AI Profit Hub</span></a>
      <ul class="nav-links" id="navLinks">
        <li><a href="../index.html">Home</a></li>
        <li><a href="../categories/tech-news.html">Tech News</a></li>
        <li><a href="../ai-tools-directory.html">AI Tools</a></li>
        <li><a href="../compare/index.html">Compare</a></li>
        <li><a href="../search.html">Search</a></li>
      </ul>
      <button class="mobile-toggle" type="button" aria-label="Toggle menu" aria-controls="navLinks" aria-expanded="false"><span></span><span></span><span></span></button>
    </nav>
  </header>
  <main class="article-page">
    <article class="article-content">
      <header class="article-header">
        <div class="article-card-tag">{html.escape(str(meta.get("category") or item.content_type.title()))}</div>
        <h1>{html.escape(title)}</h1>
        <div class="article-meta">
          <span>By {html.escape(str(meta.get("author")))}</span>
          <span>{format_date(published)}</span>
          <span>{item.reading_time} min read</span>
        </div>
      </header>
      <div class="article-cover">
        <img src="{html.escape(image_src)}" alt="{html.escape(str(meta.get("imageAlt")))}" loading="eager" fetchpriority="high" width="1200" height="675">
      </div>
      {f'<p class="disclosure-note">{disclosure}</p>' if disclosure else ''}
      <div class="article-body">
{item.html_body}
      </div>
      {sources}
      {related}
      <section class="author-box">
        <div class="author-avatar">H</div>
        <div>
          <h3>About the Author</h3>
          <p>Hussein Harby writes AI Profit Hub guides, reviews, comparisons, and analysis for readers who need practical, source-backed AI insight.</p>
        </div>
      </section>
    </article>
  </main>
  <footer class="footer">
    <div class="footer-bottom">
      <span>&copy; 2026 AI Profit Hub. All rights reserved.</span>
      <span>Built for practical AI readers.</span>
    </div>
  </footer>
  <script src="../js/main.js" defer></script>
</body>
</html>
"""


def schema_for(content_type: str) -> str:
    return {
        "news": "NewsArticle",
        "review": "Review",
        "guide": "HowTo",
        "tool": "SoftwareApplication",
        "company": "Organization",
    }.get(content_type, "Article")


def absolute_image(src: str) -> str:
    if src.startswith("https://"):
        return src
    if src.startswith("/"):
        return f"{BASE_URL}{src}"
    return f"{BASE_URL}/{src}"


def public_image_path(src: str) -> str:
    if src.startswith("https://"):
        return src
    if src.startswith("/"):
        return ".." + src
    if src.startswith("images/"):
        return "../" + src
    return src


def format_date(value: str) -> str:
    parsed = parse_date(value)
    if not parsed:
        return value
    return parsed.strftime("%B %d, %Y")


def render_sources(sources: list[Any]) -> str:
    if not sources:
        return ""
    items = []
    for source in sources:
        if isinstance(source, dict):
            title = html.escape(str(source.get("title") or source.get("url") or "Source"))
            url = html.escape(str(source.get("url") or "#"))
        else:
            title = html.escape(str(source))
            url = html.escape(str(source))
        items.append(f'<li><a href="{url}" rel="noopener noreferrer">{title}</a></li>')
    return '<section class="sources-section"><h2>Sources</h2><ul>' + "".join(items) + "</ul></section>"


def render_related(item: ContentItem) -> str:
    related = item.meta.get("related") or []
    if not related:
        return ""
    links = []
    for ref in related:
        label = html.escape(str(ref))
        slug = slugify(str(ref))
        links.append(f'<li><a href="/articles/{slug}.html">{label}</a></li>')
    return '<section class="related-content"><h2>Related Content</h2><ul>' + "".join(links) + "</ul></section>"


def extract_faq_schema(body_html: str) -> dict[str, Any] | None:
    if "<h2" not in body_html or "FAQ" not in body_html:
        return None
    pairs = []
    blocks = re.split(r"<h3[^>]*>", body_html)
    for block in blocks[1:]:
        question, _, rest = block.partition("</h3>")
        if "?" not in strip_tags(question):
            continue
        answer = strip_tags(rest.split("<h3", 1)[0]).strip()
        if answer:
            pairs.append(
                {
                    "@type": "Question",
                    "name": strip_tags(question),
                    "acceptedAnswer": {"@type": "Answer", "text": answer[:500]},
                }
            )
    if not pairs:
        return None
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": pairs}


class SearchDocumentParser(HTMLParser):
    """Extract searchable production metadata from a static HTML page."""

    SKIPPED_ELEMENTS = {"footer", "nav", "noscript", "script", "style", "svg"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.meta: dict[str, str] = {}
        self.title_parts: list[str] = []
        self.h1_parts: list[str] = []
        self.body_parts: list[str] = []
        self.in_title = False
        self.in_h1 = False
        self.in_body = False
        self.skipped_depth = 0
        self.first_time = ""
        self.has_meta_refresh = False

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        tag = tag.lower()
        values = {key.lower(): value or "" for key, value in attrs}
        if tag in self.SKIPPED_ELEMENTS:
            self.skipped_depth += 1
        if tag == "body":
            self.in_body = True
        elif tag == "title":
            self.in_title = True
        elif tag == "h1" and not self.h1_parts:
            self.in_h1 = True
        elif tag == "meta":
            key = (values.get("name") or values.get("property") or "").lower()
            content = values.get("content", "").strip()
            if key and content and key not in self.meta:
                self.meta[key] = content
            if values.get("http-equiv", "").lower() == "refresh":
                self.has_meta_refresh = True
        elif tag == "time" and not self.first_time:
            self.first_time = values.get("datetime", "").strip()

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "body":
            self.in_body = False
        elif tag == "title":
            self.in_title = False
        elif tag == "h1":
            self.in_h1 = False
        if tag in self.SKIPPED_ELEMENTS and self.skipped_depth:
            self.skipped_depth -= 1

    def handle_data(self, data: str) -> None:
        value = re.sub(r"\s+", " ", data).strip()
        if not value:
            return
        if self.in_title:
            self.title_parts.append(value)
        if self.in_h1:
            self.h1_parts.append(value)
        if self.in_body and not self.skipped_depth:
            self.body_parts.append(value)


def normalize_search_image(src: str) -> str:
    src = src.strip()
    if not src:
        return ""
    if src.startswith(("https://", "http://", "/")):
        return src
    while src.startswith("../"):
        src = src[3:]
    return "/" + src.lstrip("./")


def search_content_type(route: str) -> str:
    segment = route.strip("/").split("/", 1)[0]
    return {
        "articles": "article",
        "reviews": "review",
        "compare": "comparison",
        "guides": "guide",
        "companies": "company",
        "best-ai-tools": "tool",
        "categories": "category",
        "tutorials": "guide",
    }.get(segment, "page")


def infer_search_category(route: str, content_type: str) -> str:
    if content_type == "page":
        return "Site Page"
    return {
        "article": "Articles",
        "review": "Reviews",
        "comparison": "Compare",
        "guide": "Guides",
        "company": "Companies",
        "tool": "AI Tools",
        "category": "Categories",
    }.get(content_type, content_type.title())


def html_path_for_public_url(public_url: str) -> Path | None:
    parsed = urlparse(public_url)
    if parsed.netloc and parsed.netloc != urlparse(BASE_URL).netloc:
        return None
    route = parsed.path or "/"
    relative_path = route.lstrip("/")
    if not relative_path:
        relative_path = "index.html"
    elif route.endswith("/"):
        relative_path += "index.html"
    elif not Path(relative_path).suffix:
        relative_path += ".html"
    return ROOT / relative_path


def parse_public_html(public_url: str) -> SearchDocumentParser | None:
    path = html_path_for_public_url(public_url)
    if path is None or not path.exists() or path.suffix.lower() != ".html":
        return None
    parser = SearchDocumentParser()
    parser.feed(path.read_text(encoding="utf-8-sig"))
    return parser


def public_html_is_indexable(public_url: str) -> bool:
    parser = parse_public_html(public_url)
    if parser is None:
        return False
    return "noindex" not in parser.meta.get("robots", "").lower() and not parser.has_meta_refresh


def sitemap_html_entries() -> list[dict[str, Any]]:
    sitemap = ROOT / "sitemap.xml"
    if not sitemap.exists():
        return []
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    entries: list[dict[str, Any]] = []
    tree = ET.parse(sitemap)
    for loc in tree.findall(".//sm:loc", namespace):
        public_url = (loc.text or "").strip()
        parsed = urlparse(public_url)
        if parsed.netloc != urlparse(BASE_URL).netloc:
            continue
        route = parsed.path or "/"
        parser = parse_public_html(public_url)
        if parser is None:
            continue
        robots = parser.meta.get("robots", "").lower()
        if "noindex" in robots or parser.has_meta_refresh:
            continue
        title = " ".join(parser.h1_parts or parser.title_parts).strip()
        description = parser.meta.get("description", "").strip()
        if not title or not description:
            continue
        content_type = search_content_type(route)
        keywords = [
            value.strip()
            for value in parser.meta.get("keywords", "").split(",")
            if value.strip()
        ]
        entries.append(
            {
                "title": title,
                "url": route,
                "description": description,
                "body": " ".join(parser.body_parts)[:5000],
                "category": parser.meta.get("article:section")
                or infer_search_category(route, content_type),
                "tags": keywords,
                "contentType": content_type,
                "author": parser.meta.get("author", ""),
                "keywords": keywords,
                "image": normalize_search_image(
                    parser.meta.get("og:image")
                    or parser.meta.get("twitter:image")
                    or ""
                ),
                "date": parser.meta.get("article:published_time")
                or parser.meta.get("date")
                or parser.first_time,
            }
        )
    return entries


def write_search_index(items: list[ContentItem]) -> list[dict[str, Any]]:
    DATA.mkdir(exist_ok=True)
    by_url = {entry["url"]: entry for entry in sitemap_html_entries()}
    for item in items:
        meta = item.meta
        url = "/" + item.public_path.lstrip("/")
        by_url[url] = {
            "title": item.title,
            "url": url,
            "description": meta.get("description"),
            "body": item.body_text[:5000],
            "category": meta.get("category"),
            "tags": meta.get("tags") or [],
            "contentType": item.content_type,
            "author": meta.get("author"),
            "keywords": meta.get("keywords") or [],
            "image": normalize_search_image(str(meta.get("featuredImage") or "")),
            "date": meta.get("publishedAt") or meta.get("updatedAt"),
        }
    data = list(by_url.values())
    (DATA / "search-index.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return data


def write_related_content(
    items: list[ContentItem], search_entries: list[dict[str, Any]] | None = None
) -> None:
    del items
    data = [
        {
            "title": entry["title"],
            "url": entry["url"],
            "image": entry.get("image", ""),
            "tag": entry.get("category", ""),
            "date": format_date(str(entry.get("date") or "")),
            "contentType": entry.get("contentType", "article"),
        }
        for entry in (search_entries or [])
        if entry.get("contentType") != "page"
    ]
    (DATA / "related-content.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def update_sitemap(items: list[ContentItem], previous_paths: set[str] | None = None) -> None:
    path = ROOT / "sitemap.xml"
    ET.register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
    if path.exists():
        tree = ET.parse(path)
        root = tree.getroot()
    else:
        root = ET.Element("urlset", {"xmlns": "http://www.sitemaps.org/schemas/sitemap/0.9"})
        tree = ET.ElementTree(root)
    ns = ""
    if root.tag.startswith("{"):
        ns = root.tag.split("}", 1)[0] + "}"
    existing: dict[str | None, ET.Element] = {}
    for node in list(root.findall(f"{ns}url")):
        url = node.findtext(f"{ns}loc")
        if url in existing:
            root.remove(node)
        elif not url or not public_html_is_indexable(url):
            root.remove(node)
        else:
            existing[url] = node
    keep_urls = {item.public_url for item in items}
    stale_urls = {f"{BASE_URL}/{path}" for path in (previous_paths or set()) if f"{BASE_URL}/{path}" not in keep_urls}
    for url in stale_urls:
        node = existing.get(url)
        if node is not None:
            root.remove(node)
    for item in items:
        node = existing.get(item.public_url)
        if node is None:
            node = ET.Element(f"{ns}url")
            loc = ET.SubElement(node, f"{ns}loc")
            loc.text = item.public_url
            root.insert(0, node)
        set_child(node, ns, "lastmod", iso_utc(str(item.meta.get("updatedAt") or item.meta.get("publishedAt"))))
        set_child(node, ns, "changefreq", "monthly")
        set_child(node, ns, "priority", "0.8")
    indent_xml(root)
    tree.write(path, encoding="utf-8", xml_declaration=True)


def set_child(node: ET.Element, ns: str, name: str, value: str) -> None:
    child = node.find(f"{ns}{name}")
    if child is None:
        child = ET.SubElement(node, f"{ns}{name}")
    child.text = value


def update_rss(items: list[ContentItem], previous_paths: set[str] | None = None) -> None:
    path = ROOT / "rss.xml"
    ET.register_namespace("atom", "http://www.w3.org/2005/Atom")
    if path.exists():
        tree = ET.parse(path)
        root = tree.getroot()
        channel = root.find("channel")
        if channel is None:
            channel = ET.SubElement(root, "channel")
    else:
        root = ET.Element("rss", {"version": "2.0"})
        channel = ET.SubElement(root, "channel")
        tree = ET.ElementTree(root)
    existing: dict[str | None, ET.Element] = {}
    for node in list(channel.findall("item")):
        url = node.findtext("guid") or node.findtext("link")
        if url in existing:
            channel.remove(node)
        elif not url or not public_html_is_indexable(url):
            channel.remove(node)
        else:
            existing[url] = node
    keep_urls = {item.public_url for item in items}
    stale_urls = {f"{BASE_URL}/{path}" for path in (previous_paths or set()) if f"{BASE_URL}/{path}" not in keep_urls}
    for url in stale_urls:
        node = existing.get(url)
        if node is not None:
            channel.remove(node)
    for item in items:
        if item.content_type not in RSS_TYPES:
            continue
        node = existing.get(item.public_url)
        if node is None:
            node = ET.Element("item")
            channel.insert(0, node)
        set_plain_child(node, "title", item.title)
        set_plain_child(node, "link", item.public_url)
        set_plain_child(node, "description", str(item.meta.get("description") or ""))
        set_plain_child(node, "pubDate", rss_date(str(item.meta.get("publishedAt") or item.meta.get("updatedAt"))))
        set_plain_child(node, "guid", item.public_url)
    indent_xml(root)
    tree.write(path, encoding="utf-8", xml_declaration=True)


def set_plain_child(node: ET.Element, name: str, value: str) -> None:
    child = node.find(name)
    if child is None:
        child = ET.SubElement(node, name)
    child.text = value


def iso_utc(value: str) -> str:
    parsed = parse_date(value) or dt.datetime.now(dt.timezone.utc)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def rss_date(value: str) -> str:
    parsed = parse_date(value) or dt.datetime.now(dt.timezone.utc)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone(dt.timedelta(hours=3))).strftime("%a, %d %b %Y %H:%M:%S +0300")


def indent_xml(elem: ET.Element, level: int = 0) -> None:
    pad = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = pad + "  "
        for child in elem:
            indent_xml(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = pad
    if level and (not elem.tail or not elem.tail.strip()):
        elem.tail = pad


def report() -> int:
    items = load_content()
    threshold_days = 180
    now = dt.datetime.now(dt.timezone.utc)
    print("Content report")
    print("==============")
    for status in sorted(ALLOWED_STATUS):
        count = sum(1 for item in items if item.status == status)
        print(f"{status}: {count}")
    print("\nPotentially outdated content:")
    for item in items:
        value = str(item.meta.get("lastReviewed") or item.meta.get("updatedAt") or "")
        parsed = parse_date(value)
        if parsed:
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=dt.timezone.utc)
            if (now - parsed.astimezone(dt.timezone.utc)).days > threshold_days:
                print(f"- {item.path.relative_to(ROOT)} last reviewed {value}")
    return 0


def audit() -> int:
    html_count = len(list(ROOT.rglob("*.html")))
    article_count = len(list((ROOT / "articles").glob("*.html"))) if (ROOT / "articles").exists() else 0
    md_count = len(list(CONTENT.rglob("*.md"))) if CONTENT.exists() else 0
    print("Project audit")
    print("=============")
    print("Framework: Static HTML, CSS, and JavaScript")
    print("Runtime: No package runtime required for production pages")
    print("Build system: Historically manual/static; this content pipeline adds Markdown generation")
    print("Routing: File-based static routes")
    print("Deployment: GitHub main branch deploys through Vercel")
    print(f"HTML files: {html_count}")
    print(f"Article HTML files: {article_count}")
    print(f"Content Markdown files: {md_count}")
    print("Search: Sitemap-backed data/search-index.json with a legacy inline fallback")
    print("Sitemap: sitemap.xml in the site root")
    print("RSS: rss.xml in the site root")
    print("Images: Production images are stored in images/")
    return 0


def route_check() -> int:
    items = [item for item in load_content() if item.is_published]
    missing = []
    for item in items:
        if not (ROOT / item.public_path).exists():
            missing.append(item.public_path)
    if missing:
        for path in missing:
            print(f"ERROR: generated route missing: {path}")
        return 1
    print(f"Route check passed for {len(items)} generated route(s).")
    return 0


def render_preview_html(item: ContentItem, items: list[ContentItem]) -> str:
    lookup = build_lookup(items)
    item.html_body = render_markdown(item.body, lookup)
    item.body_text = strip_tags(item.html_body)
    page = render_page(item)
    return re.sub(
        r'<meta\s+name="robots"\s+content="[^"]*">',
        '<meta name="robots" content="noindex, nofollow">',
        page,
        count=1,
        flags=re.I,
    )


def select_preview_item(items: list[ContentItem], selector: str) -> ContentItem | None:
    normalized = selector.replace("\\", "/").strip().strip("/")
    matches = []
    for item in items:
        relative = item.path.relative_to(CONTENT).as_posix()
        if normalized in {relative, item.path.name, item.slug, item.title}:
            matches.append(item)
    if len(matches) > 1:
        names = ", ".join(item.path.relative_to(ROOT).as_posix() for item in matches)
        fail(f"Preview selector is ambiguous: {names}")
        return None
    if not matches:
        fail(f"Preview content was not found: {selector}")
        return None
    return matches[0]


def preview_draft(selector: str, port: int) -> int:
    items = load_content()
    if validate(items) != 0:
        return 1
    item = select_preview_item(items, selector)
    if item is None:
        return 1
    preview_html = render_preview_html(item, items).encode("utf-8")
    preview_path = f"/__obsidian_preview__/{item.slug}.html"

    class DraftPreviewHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, directory=str(ROOT), **kwargs)

        def do_GET(self) -> None:
            if unquote(urlparse(self.path).path) == preview_path:
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(preview_html)))
                self.end_headers()
                self.wfile.write(preview_html)
                return
            super().do_GET()

        def end_headers(self) -> None:
            self.send_header("X-Robots-Tag", "noindex, nofollow")
            super().end_headers()

    server = ThreadingHTTPServer(("127.0.0.1", port), DraftPreviewHandler)
    print(f"Draft preview: http://127.0.0.1:{port}{preview_path}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Preview stopped.")
    finally:
        server.server_close()
    return 0


def preview(port: int) -> int:
    if build() != 0:
        return 1
    class Handler(SimpleHTTPRequestHandler):
        def end_headers(self) -> None:
            self.send_header("X-Robots-Tag", "noindex, nofollow")
            super().end_headers()

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Preview server running at http://127.0.0.1:{port}/")
    print("Press Ctrl+C to stop.")
    old_cwd = Path.cwd()
    import os

    try:
        os.chdir(ROOT)
        server.serve_forever()
    except KeyboardInterrupt:
        print("Preview stopped.")
    finally:
        os.chdir(old_cwd)
    return 0


def publish_check() -> int:
    steps = [
        ("audit", audit),
        ("build", build),
        ("route-check", route_check),
        ("site-audit", lambda: run_python_script("site_audit.py")),
    ]
    for name, fn in steps:
        print(f"\nRunning {name}...")
        code = fn()
        if code != 0:
            fail(f"publish-content failed at {name}")
            return code
    print("\nPublish checks passed. Review the Git diff, then commit and push when ready.")
    return 0


def run_python_script(script_name: str) -> int:
    script = ROOT / "scripts" / script_name
    result = subprocess.run([sys.executable, str(script)], cwd=ROOT)
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="AI Profit Hub content pipeline")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("audit")
    sub.add_parser("validate")
    sub.add_parser("build")
    sub.add_parser("report")
    sub.add_parser("route-check")
    sub.add_parser("publish-check")
    preview_parser = sub.add_parser("preview")
    preview_parser.add_argument("--port", type=int, default=8787)
    draft_preview_parser = sub.add_parser("preview-draft")
    draft_preview_parser.add_argument("selector")
    draft_preview_parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()
    if args.command == "audit":
        return audit()
    if args.command == "validate":
        return validate(load_content())
    if args.command == "build":
        return build()
    if args.command == "report":
        return report()
    if args.command == "route-check":
        return route_check()
    if args.command == "publish-check":
        return publish_check()
    if args.command == "preview":
        return preview(args.port)
    if args.command == "preview-draft":
        return preview_draft(args.selector, args.port)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
