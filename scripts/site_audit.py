#!/usr/bin/env python3
"""Production safety audit for the AI Profit Hub static site."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = "https://ai-profit-hub.com"
TEXT_EXTENSIONS = {".html", ".css", ".js", ".json", ".xml", ".txt", ".md", ".py", ".ps1"}
ALLOWED_NOINDEX = {"404.html", "dashboard.html", "reviews/review-template.html"}
SECRET_FILE_PATTERNS = {
    ".env",
    ".env.local",
    ".env.production",
    "credentials.json",
    "service-account.json",
    "scripts/service-account.json",
}


class AssetParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str, int]] = []
        self.images: list[tuple[str, str, int]] = []
        self.titles = 0
        self.descriptions = 0
        self.canonicals = 0
        self.noindex = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key.lower(): value or "" for key, value in attrs}
        line, _ = self.getpos()
        if tag == "a" and data.get("href"):
            self.links.append((data["href"], data.get("aria-label", ""), line))
        if tag == "img":
            self.images.append((data.get("src", ""), data.get("alt", ""), line))
        if tag == "meta" and data.get("name", "").lower() == "description":
            self.descriptions += 1
        if tag == "meta" and data.get("name", "").lower() == "robots" and "noindex" in data.get("content", "").lower():
            self.noindex = True
        if tag == "link" and data.get("rel", "").lower() == "canonical":
            self.canonicals += 1

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_data(self, data: str) -> None:
        pass


def tracked_files() -> list[Path]:
    result = subprocess.run(["git", "ls-files"], cwd=ROOT, text=True, capture_output=True, check=True)
    return [ROOT / line for line in result.stdout.splitlines() if line.strip()]


def is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTENSIONS


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def local_target_exists(url: str, current_file: Path) -> bool:
    parsed = urlparse(url)
    if parsed.scheme in {"mailto", "tel", "javascript"}:
        return True
    if parsed.scheme in {"http", "https"}:
        if parsed.netloc != "ai-profit-hub.com":
            return True
        url_path = parsed.path
    else:
        url_path = parsed.path

    if not url_path or url_path == "#":
        return True
    url_path = unquote(url_path.split("#", 1)[0].split("?", 1)[0])
    if not url_path:
        return True
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


def check_xml(errors: list[str]) -> None:
    for name in ("sitemap.xml", "rss.xml"):
        try:
            ET.parse(ROOT / name)
        except Exception as exc:
            errors.append(f"{name}: invalid XML: {exc}")


def check_json(errors: list[str]) -> None:
    for name in ("data/search-index.json", "data/related-content.json", "data/content-manifest.json", "vercel.json"):
        path = ROOT / name
        if path.exists():
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                errors.append(f"{name}: invalid JSON: {exc}")


def check_html(errors: list[str], warnings: list[str]) -> None:
    html_files = [path for path in tracked_files() if path.exists() and path.suffix.lower() == ".html"]
    broken_links = []
    broken_images = []
    missing_alt = []
    for path in html_files:
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = relative(path)
        if "https://ai-profit-hub.comhttps://" in text:
            errors.append(f"{rel}: malformed absolute URL contains duplicated scheme")
        parser = AssetParser()
        parser.feed(text)
        if "<title>" not in text.lower():
            warnings.append(f"{rel}: missing title tag")
        if parser.descriptions == 0:
            warnings.append(f"{rel}: missing meta description")
        if parser.canonicals == 0:
            warnings.append(f"{rel}: missing canonical link")
        if parser.noindex and rel not in ALLOWED_NOINDEX:
            warnings.append(f"{rel}: has noindex")
        for href, _, line in parser.links:
            if not local_target_exists(href, path):
                broken_links.append(f"{rel}:{line} -> {href}")
        for src, alt, line in parser.images:
            if src and not local_target_exists(src, path):
                broken_images.append(f"{rel}:{line} -> {src}")
            if src and not alt.strip():
                missing_alt.append(f"{rel}:{line} -> {src}")
    for item in broken_links[:50]:
        warnings.append(f"broken internal link: {item}")
    for item in broken_images[:50]:
        warnings.append(f"broken image reference: {item}")
    for item in missing_alt[:50]:
        warnings.append(f"image missing alt text: {item}")
    if len(broken_links) > 50:
        warnings.append(f"{len(broken_links) - 50} additional broken internal links were omitted")
    if len(broken_images) > 50:
        warnings.append(f"{len(broken_images) - 50} additional broken image references were omitted")


def check_language(warnings: list[str]) -> None:
    arabic_files = []
    for path in tracked_files():
        if not path.exists():
            continue
        if not is_text_file(path):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if any("\u0600" <= char <= "\u06ff" for char in text):
            arabic_files.append(relative(path))
    if arabic_files:
        warnings.append(f"{len(arabic_files)} tracked text file(s) contain Arabic script and need a separate editorial migration")


def check_secrets(errors: list[str], warnings: list[str]) -> None:
    tracked = {relative(path) for path in tracked_files()}
    for pattern in SECRET_FILE_PATTERNS:
        if pattern in tracked:
            errors.append(f"secret-looking file is tracked: {pattern}")
        elif (ROOT / pattern).exists():
            warnings.append(f"local secret-looking file exists but is not tracked: {pattern}")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    check_xml(errors)
    check_json(errors)
    check_html(errors, warnings)
    check_language(warnings)
    check_secrets(errors, warnings)

    print("Site audit")
    print("==========")
    print(f"Errors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    for item in errors:
        print(f"ERROR: {item}")
    for item in warnings:
        print(f"WARNING: {item}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
