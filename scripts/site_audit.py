#!/usr/bin/env python3
"""Production safety audit for the AI Profit Hub static site."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = "https://ai-profit-hub.com"
TEXT_EXTENSIONS = {
    ".css",
    ".csv",
    ".html",
    ".js",
    ".json",
    ".md",
    ".ps1",
    ".py",
    ".toml",
    ".ts",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}
NON_PRODUCTION_HTML = {
    "article-template.html",
    "reviews/review-template.html",
}
IMAGE_EXTENSIONS = {".avif", ".gif", ".jpeg", ".jpg", ".png", ".svg", ".webp"}
ALLOWED_NOINDEX = {
    "404.html",
    "dashboard.html",
    *NON_PRODUCTION_HTML,
}
SECRET_FILE_PATTERNS = {
    ".env",
    ".env.local",
    ".env.production",
    "credentials.json",
    "service-account.json",
    "scripts/service-account.json",
}
ARABIC_RE = re.compile(
    "[\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff\ufb50-\ufdff\ufe70-\ufefc]"
)
MOJIBAKE_RE = re.compile(
    r"\ufffd|\u00c3.|\u00c2.|\u00e2[\u20ac-\u2122]|\u00f0\u0178|\u00ef\u00bf\u00bd"
)
JSON_LD_RE = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.IGNORECASE | re.DOTALL,
)
META_REFRESH_TAG_RE = re.compile(
    r'<meta\b(?=[^>]*http-equiv=["\']refresh["\'])[^>]*>',
    re.IGNORECASE,
)
META_CONTENT_RE = re.compile(
    r'content=(?P<quote>["\'])(?P<value>.*?)(?P=quote)',
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Issue:
    severity: str
    category: str
    message: str
    file_path: str = ""
    line: int = 0

    def display(self) -> str:
        location = self.file_path
        if location and self.line:
            location = f"{location}:{self.line}"
        if location:
            return f"{location}: {self.message}"
        return self.message


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, int]] = []
        self.images: list[tuple[str, str, int]] = []
        self.metadata_images: list[tuple[str, str, int]] = []
        self.titles: list[str] = []
        self.descriptions: list[str] = []
        self.canonicals: list[str] = []
        self.noindex = False
        self.meta_refresh = False
        self._in_title = False
        self._title_parts: list[str] = []
        self._in_head = False
        self._ignored_head_depth = 0
        self.head_text: list[tuple[str, int]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key.lower(): value or "" for key, value in attrs}
        line, _ = self.getpos()
        tag = tag.lower()
        if tag == "head":
            self._in_head = True
        elif self._in_head and tag in {"noscript", "script", "style", "title"}:
            self._ignored_head_depth += 1
        if tag == "title":
            self._in_title = True
            self._title_parts = []
        if tag == "a" and data.get("href"):
            self.links.append((data["href"], line))
        if tag == "img":
            self.images.append((data.get("src", ""), data.get("alt", ""), line))
        if tag == "meta" and data.get("name", "").lower() == "description":
            self.descriptions.append(data.get("content", "").strip())
        meta_key = (
            data.get("property", "") or data.get("name", "")
        ).lower()
        if meta_key in {"og:image", "twitter:image"}:
            self.metadata_images.append((meta_key, data.get("content", "").strip(), line))
        if (
            tag == "meta"
            and data.get("name", "").lower() == "robots"
            and "noindex" in data.get("content", "").lower()
        ):
            self.noindex = True
        if tag == "meta" and data.get("http-equiv", "").lower() == "refresh":
            self.meta_refresh = True
        if tag == "link" and "canonical" in data.get("rel", "").lower().split():
            self.canonicals.append(data.get("href", "").strip())

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title" and self._in_title:
            self.titles.append(" ".join("".join(self._title_parts).split()))
            self._in_title = False
        if self._in_head and tag in {"noscript", "script", "style", "title"}:
            self._ignored_head_depth = max(0, self._ignored_head_depth - 1)
        if tag == "head":
            self._in_head = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._title_parts.append(data)
        value = " ".join(data.split())
        if self._in_head and not self._ignored_head_depth and value:
            line, _ = self.getpos()
            self.head_text.append((value, line))


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    return [
        ROOT / raw.decode("utf-8", errors="surrogateescape")
        for raw in result.stdout.split(b"\0")
        if raw
    ]


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTENSIONS


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def read_text(path: Path, issues: list[Issue]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        issues.append(
            Issue(
                "error",
                "encoding_corruption",
                f"file is not valid UTF-8 ({exc.reason})",
                relative(path),
                1,
            )
        )
        return path.read_text(encoding="utf-8", errors="replace")


def local_target_exists(url: str, current_file: Path) -> bool:
    parsed = urlparse(url)
    if parsed.scheme in {"mailto", "tel", "javascript", "data"}:
        return True
    if parsed.scheme in {"http", "https"}:
        if parsed.netloc.lower() not in {"ai-profit-hub.com", "www.ai-profit-hub.com"}:
            return True
        url_path = parsed.path
    else:
        url_path = parsed.path

    if not url_path or url_path == "#":
        return True
    url_path = unquote(url_path)
    if url_path.startswith("/"):
        target = ROOT / url_path.lstrip("/")
    else:
        target = current_file.parent / url_path
    if target.is_dir():
        target = target / "index.html"
    if target.suffix == "":
        if (target / "index.html").exists():
            return True
        target = target.with_suffix(".html")
    return target.exists()


def redirect_target(text: str) -> str:
    tag = META_REFRESH_TAG_RE.search(text)
    if not tag:
        return ""
    content = META_CONTENT_RE.search(tag.group(0))
    if not content:
        return ""
    match = re.search(r"url\s*=\s*(.+)", content.group("value"), re.IGNORECASE)
    return match.group(1).strip().strip("\"'") if match else ""


def valid_metadata_image(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        return False
    if parsed.netloc.lower() not in {"ai-profit-hub.com", "www.ai-profit-hub.com"}:
        return True
    target = ROOT / unquote(parsed.path).lstrip("/")
    return target.exists() and target.is_file() and target.suffix.lower() in IMAGE_EXTENSIONS


def validate_redirect_graph(
    redirect_map: dict[str, str],
    issues: list[Issue],
    source_label: str,
) -> None:
    for source, destination in redirect_map.items():
        seen = {source}
        current = destination
        while current in redirect_map:
            if current in seen:
                issues.append(
                    Issue(
                        "error",
                        "invalid_redirect",
                        f"redirect loop detected from {source}",
                        source_label,
                    )
                )
                break
            seen.add(current)
            current = redirect_map[current]
        if destination in redirect_map:
            issues.append(
                Issue(
                    "warning",
                    "invalid_redirect",
                    f"redirect chain should point directly to {current}: {source} -> {destination}",
                    source_label,
                )
            )


def check_xml(issues: list[Issue]) -> None:
    for name in ("sitemap.xml", "rss.xml"):
        try:
            ET.parse(ROOT / name)
        except Exception as exc:
            issues.append(Issue("error", "xml_issue", f"invalid XML: {exc}", name))


def check_json(files: list[Path], issues: list[Issue]) -> None:
    for path in files:
        if not path.exists() or path.suffix.lower() != ".json":
            continue
        text = read_text(path, issues)
        try:
            json.loads(text.lstrip("\ufeff"))
        except Exception as exc:
            issues.append(
                Issue("error", "json_issue", f"invalid JSON: {exc}", relative(path))
            )


def check_vercel(issues: list[Issue]) -> dict[str, str]:
    path = ROOT / "vercel.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}
    redirect_map: dict[str, str] = {}
    for index, item in enumerate(data.get("redirects", []), 1):
        source = str(item.get("source", "")).strip()
        destination = str(item.get("destination", "")).strip()
        if not source.startswith("/") or not destination.startswith("/"):
            issues.append(
                Issue(
                    "error",
                    "invalid_redirect",
                    f"redirect {index} must use root-relative source and destination",
                    "vercel.json",
                )
            )
            continue
        if item.get("permanent") is not True:
            issues.append(
                Issue(
                    "warning",
                    "invalid_redirect",
                    f"redirect {source} is not permanent",
                    "vercel.json",
                )
            )
        redirect_map[source] = destination
    validate_redirect_graph(redirect_map, issues, "vercel.json")
    if redirect_map.get("/index.html") != "/":
        issues.append(
            Issue(
                "error",
                "invalid_redirect",
                "/index.html must permanently redirect to /",
                "vercel.json",
            )
        )
    return redirect_map


def check_canonical(
    canonical: str,
    path: Path,
    issues: list[Issue],
) -> None:
    rel = relative(path)
    parsed = urlparse(canonical)
    if parsed.scheme != "https" or parsed.netloc.lower() != "ai-profit-hub.com":
        issues.append(
            Issue(
                "warning",
                "invalid_canonical",
                f"canonical must use the production HTTPS domain: {canonical}",
                rel,
            )
        )
        return
    if "https://" in parsed.path or not parsed.path:
        issues.append(
            Issue(
                "warning",
                "invalid_canonical",
                f"canonical path is malformed: {canonical}",
                rel,
            )
        )
        return
    if rel == "index.html":
        expected_paths = {"/", "/index.html"}
    elif rel.endswith("/index.html"):
        directory = "/" + rel.removesuffix("index.html")
        expected_paths = {directory, "/" + rel}
    else:
        expected_paths = {"/" + rel}
    if parsed.path not in expected_paths:
        issues.append(
            Issue(
                "warning",
                "invalid_canonical",
                f"canonical path does not match the page route: {canonical}",
                rel,
            )
        )


def check_json_ld(text: str, path: Path, issues: list[Issue]) -> None:
    rel = relative(path)
    for match in JSON_LD_RE.finditer(text):
        raw = match.group(1).strip()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            issues.append(
                Issue(
                    "warning",
                    "structured_data_issue",
                    f"invalid JSON-LD: {exc.msg}",
                    rel,
                    line_number(text, match.start()),
                )
            )
            continue
        serialized = json.dumps(data, ensure_ascii=False)
        if (
            "https://ai-profit-hub.comhttps://" in serialized
            or "https://ai-profit-hub.com//" in serialized
            or "..https://" in serialized
        ):
            issues.append(
                Issue(
                    "warning",
                    "structured_data_issue",
                    "JSON-LD contains a malformed absolute URL",
                    rel,
                    line_number(text, match.start()),
                )
            )


def check_html(files: list[Path], issues: list[Issue]) -> None:
    html_files = [
        path for path in files if path.exists() and path.suffix.lower() == ".html"
    ]
    titles: dict[str, list[str]] = {}
    descriptions: dict[str, list[str]] = {}

    for path in html_files:
        rel = relative(path)
        text = read_text(path, issues)
        if "https://ai-profit-hub.comhttps://" in text or "..https://" in text:
            issues.append(
                Issue(
                    "error",
                    "malformed_url",
                    "contains a malformed duplicated absolute URL",
                    rel,
                )
            )

        parser = PageParser()
        try:
            parser.feed(text)
        except Exception as exc:
            issues.append(
                Issue("warning", "html_issue", f"HTML parser failed: {exc}", rel)
            )
            continue
        for value, line in parser.head_text:
            issues.append(
                Issue(
                    "warning",
                    "html_issue",
                    f"visible text is not allowed inside head: {value[:80]}",
                    rel,
                    line,
                )
            )

        redirect = redirect_target(text)
        if redirect:
            if not local_target_exists(redirect, path):
                issues.append(
                    Issue(
                        "warning",
                        "invalid_redirect",
                        f"meta refresh target does not exist: {redirect}",
                        rel,
                    )
                )
            continue

        is_template = rel in NON_PRODUCTION_HTML
        if is_template and not parser.noindex:
            issues.append(
                Issue(
                    "warning",
                    "publication_status_issue",
                    "authoring template must include noindex",
                    rel,
                )
            )

        if not is_template:
            if len(parser.titles) != 1 or not parser.titles[0]:
                issues.append(
                    Issue("warning", "missing_title", "missing title tag", rel)
                )
            else:
                titles.setdefault(parser.titles[0].casefold(), []).append(rel)
            if len(parser.descriptions) != 1 or not parser.descriptions[0]:
                issues.append(
                    Issue(
                        "warning",
                        "missing_meta_description",
                        "missing meta description",
                        rel,
                    )
                )
            else:
                descriptions.setdefault(
                    parser.descriptions[0].casefold(), []
                ).append(rel)
            if len(parser.canonicals) != 1 or not parser.canonicals[0]:
                issues.append(
                    Issue(
                        "warning",
                        "missing_canonical",
                        "missing canonical link",
                        rel,
                    )
                )
            else:
                check_canonical(parser.canonicals[0], path, issues)
            if parser.noindex and rel not in ALLOWED_NOINDEX:
                issues.append(
                    Issue(
                        "warning",
                        "publication_status_issue",
                        "unexpected noindex on a production page",
                        rel,
                    )
                )

        if not is_template:
            for href, line in parser.links:
                if not local_target_exists(href, path):
                    issues.append(
                        Issue(
                            "warning",
                            "broken_internal_link",
                            f"broken internal link: {href}",
                            rel,
                            line,
                        )
                    )
            for src, alt, line in parser.images:
                if not src:
                    issues.append(
                        Issue(
                            "warning",
                            "broken_image",
                            "image is missing a src value",
                            rel,
                            line,
                        )
                    )
                    continue
                if not local_target_exists(src, path):
                    issues.append(
                        Issue(
                            "warning",
                            "broken_image",
                            f"broken image reference: {src}",
                            rel,
                            line,
                        )
                    )
                if not alt.strip():
                    issues.append(
                        Issue(
                            "warning",
                            "missing_image_alt",
                            f"image is missing alt text: {src}",
                            rel,
                            line,
                        )
                    )
            for kind, src, line in parser.metadata_images:
                if not valid_metadata_image(src):
                    issues.append(
                        Issue(
                            "warning",
                            "broken_image",
                            f"{kind} must use a valid absolute HTTPS image URL: {src}",
                            rel,
                            line,
                        )
                    )
            check_json_ld(text, path, issues)

    for value, paths in titles.items():
        if len(paths) > 1:
            for path in paths:
                issues.append(
                    Issue(
                        "warning",
                        "duplicate_title",
                        f"title is duplicated across {len(paths)} pages",
                        path,
                    )
                )
    for value, paths in descriptions.items():
        if value and len(paths) > 1:
            for path in paths:
                issues.append(
                    Issue(
                        "warning",
                        "duplicate_meta_description",
                        f"meta description is duplicated across {len(paths)} pages",
                        path,
                    )
                )


def check_language_and_encoding(files: list[Path], issues: list[Issue]) -> None:
    for path in files:
        if not path.exists() or not is_text_file(path):
            continue
        text = read_text(path, issues)
        rel = relative(path)
        for number, line in enumerate(text.splitlines(), 1):
            if ARABIC_RE.search(line):
                issues.append(
                    Issue(
                        "error",
                        "arabic_script",
                        "Arabic script is not allowed in tracked project text",
                        rel,
                        number,
                    )
                )
            if MOJIBAKE_RE.search(line):
                issues.append(
                    Issue(
                        "warning",
                        "encoding_corruption",
                        "contains a replacement character or likely mojibake",
                        rel,
                        number,
                    )
                )


def check_sitemap_and_rss(issues: list[Issue]) -> None:
    sitemap_path = ROOT / "sitemap.xml"
    try:
        tree = ET.parse(sitemap_path)
    except Exception:
        return
    root = tree.getroot()
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [
        node.text.strip()
        for node in root.findall("sm:url/sm:loc", namespace)
        if node.text
    ]
    for url in sorted({url for url in urls if urls.count(url) > 1}):
        issues.append(
            Issue("warning", "sitemap_issue", f"duplicate sitemap URL: {url}", "sitemap.xml")
        )
    for url in urls:
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.netloc != "ai-profit-hub.com":
            issues.append(
                Issue(
                    "warning",
                    "sitemap_issue",
                    f"invalid canonical-domain URL: {url}",
                    "sitemap.xml",
                )
            )
        elif not local_target_exists(url, sitemap_path):
            issues.append(
                Issue(
                    "warning",
                    "sitemap_issue",
                    f"URL does not map to a tracked public page: {url}",
                    "sitemap.xml",
                )
            )
        else:
            target = ROOT / unquote(parsed.path).lstrip("/")
            if target.is_dir():
                target = target / "index.html"
            if not target.suffix:
                target = target.with_suffix(".html")
            if target.exists() and target.suffix.lower() == ".html":
                text = target.read_text(encoding="utf-8-sig")
                parser = PageParser()
                parser.feed(text)
                if parser.noindex or parser.meta_refresh:
                    issues.append(
                        Issue(
                            "warning",
                            "sitemap_issue",
                            f"non-indexable page is listed: {url}",
                            "sitemap.xml",
                        )
                    )

    rss_path = ROOT / "rss.xml"
    try:
        rss_tree = ET.parse(rss_path)
    except Exception:
        return
    links = [
        node.text.strip()
        for node in rss_tree.findall("./channel/item/link")
        if node.text
    ]
    for url in sorted({url for url in links if links.count(url) > 1}):
        issues.append(
            Issue("warning", "rss_issue", f"duplicate RSS item URL: {url}", "rss.xml")
        )
    for url in links:
        if not local_target_exists(url, rss_path):
            issues.append(
                Issue(
                    "warning",
                    "rss_issue",
                    f"item URL does not map to a tracked public page: {url}",
                    "rss.xml",
                )
            )
            continue
        parsed = urlparse(url)
        target = ROOT / unquote(parsed.path).lstrip("/")
        if target.is_dir():
            target = target / "index.html"
        if not target.suffix:
            target = target.with_suffix(".html")
        if target.exists() and target.suffix.lower() == ".html":
            text = target.read_text(encoding="utf-8-sig")
            parser = PageParser()
            parser.feed(text)
            if parser.noindex or parser.meta_refresh:
                issues.append(
                    Issue(
                        "warning",
                        "rss_issue",
                        f"non-indexable page is listed: {url}",
                        "rss.xml",
                    )
                )


def check_search_and_related(issues: list[Issue]) -> None:
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    searchable_prefixes = (
        "/articles/",
        "/best-ai-tools/",
        "/categories/",
        "/companies/",
        "/compare/",
        "/guides/",
        "/reviews/",
        "/tutorials/",
    )
    try:
        sitemap_routes = {
            urlparse((node.text or "").strip()).path or "/"
            for node in ET.parse(ROOT / "sitemap.xml").findall(".//sm:loc", namespace)
            if node.text
        }
    except Exception:
        sitemap_routes = set()
    expected_content_routes = {
        route for route in sitemap_routes if route.startswith(searchable_prefixes)
    }

    for name in ("data/search-index.json", "data/related-content.json"):
        path = ROOT / name
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception:
            continue
        if not isinstance(data, list):
            issues.append(
                Issue("error", "search_index_issue", "root must be a JSON array", name)
            )
            continue
        if not data:
            issues.append(
                Issue(
                    "warning",
                    "search_index_issue",
                    "production index must not be empty",
                    name,
                )
            )
        seen: set[str] = set()
        for index, item in enumerate(data):
            if not isinstance(item, dict):
                issues.append(
                    Issue(
                        "warning",
                        "search_index_issue",
                        f"entry {index} must be an object",
                        name,
                    )
                )
                continue
            required = {"title", "url"}
            if name == "data/search-index.json":
                required |= {"description", "contentType"}
            for field in sorted(required):
                if not str(item.get(field, "")).strip():
                    issues.append(
                        Issue(
                            "warning",
                            "search_index_issue",
                            f"entry {index} is missing {field}",
                            name,
                        )
                    )
            url = str(item.get("url", "")).strip()
            if not url or not local_target_exists(url, path):
                issues.append(
                    Issue(
                        "warning",
                        "search_index_issue",
                        f"entry {index} has an invalid public URL: {url}",
                        name,
                    )
                )
            if url in seen:
                issues.append(
                    Issue(
                        "warning",
                        "search_index_issue",
                        f"duplicate public URL: {url}",
                        name,
                    )
                )
            seen.add(url)
        missing_routes = expected_content_routes - seen
        for url in sorted(missing_routes):
            issues.append(
                Issue(
                    "warning",
                    "search_index_issue",
                    f"indexed sitemap content is missing: {url}",
                    name,
                )
            )


def check_secrets(files: list[Path], issues: list[Issue], info: list[str]) -> None:
    tracked = {relative(path) for path in files}
    for pattern in sorted(SECRET_FILE_PATTERNS):
        if pattern in tracked:
            issues.append(
                Issue(
                    "error",
                    "tracked_secret",
                    "secret-looking file is tracked",
                    pattern,
                )
            )
        elif (ROOT / pattern).exists():
            info.append(f"protected local credential remains ignored and untracked: {pattern}")


def write_json_report(path: Path, issues: list[Issue], info: list[str]) -> None:
    payload = {
        "errors": sum(issue.severity == "error" for issue in issues),
        "warnings": sum(issue.severity == "warning" for issue in issues),
        "issues": [asdict(issue) for issue in issues],
        "info": info,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-report", type=Path)
    args = parser.parse_args()

    issues: list[Issue] = []
    info: list[str] = []
    files = tracked_files()

    check_xml(issues)
    check_json(files, issues)
    check_vercel(issues)
    check_html(files, issues)
    check_language_and_encoding(files, issues)
    check_sitemap_and_rss(issues)
    check_search_and_related(issues)
    check_secrets(files, issues, info)

    issues = list(dict.fromkeys(issues))
    errors = [issue for issue in issues if issue.severity == "error"]
    warnings = [issue for issue in issues if issue.severity == "warning"]
    print("Site audit")
    print("==========")
    print(f"Errors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    for issue in errors:
        print(f"ERROR [{issue.category}]: {issue.display()}")
    for issue in warnings:
        print(f"WARNING [{issue.category}]: {issue.display()}")
    for item in info:
        print(f"INFO: {item}")

    if args.json_report:
        report_path = args.json_report
        if not report_path.is_absolute():
            report_path = ROOT / report_path
        write_json_report(report_path, issues, info)

    return 1 if errors or warnings else 0


if __name__ == "__main__":
    raise SystemExit(main())
