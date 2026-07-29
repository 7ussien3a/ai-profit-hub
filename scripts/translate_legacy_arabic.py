#!/usr/bin/env python3
"""Translate Arabic text in legacy HTML pages while preserving page structure."""

from __future__ import annotations

import argparse
import html
import json
import re
import tempfile
import time
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup, Comment, NavigableString

ROOT = Path(__file__).resolve().parent.parent
CACHE_PATH = Path(tempfile.gettempdir()) / "ai-profit-hub-translation-cache.json"
TRANSLATE_URL = "https://translate.googleapis.com/translate_a/single"
FALLBACK_TRANSLATE_URL = "https://api.mymemory.translated.net/get"
ARABIC_RE = re.compile(
    "[\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff\ufb50-\ufdff\ufe70-\ufefc]"
)
MARKER_RE = re.compile(r"\[\[\[AI_PROFIT_HUB_(\d{4})\]\]\]")
MAX_BATCH_CHARS = 3_600
ARABIC_NORMALIZATION = str.maketrans(
    {
        "\u060c": ",",
        "\u061b": ";",
        "\u061f": "?",
        "\u0640": "",
        "\u0660": "0",
        "\u0661": "1",
        "\u0662": "2",
        "\u0663": "3",
        "\u0664": "4",
        "\u0665": "5",
        "\u0666": "6",
        "\u0667": "7",
        "\u0668": "8",
        "\u0669": "9",
        "\u066a": "%",
        "\u066b": ".",
        "\u066c": ",",
        "\u06d4": ".",
        "\u06f0": "0",
        "\u06f1": "1",
        "\u06f2": "2",
        "\u06f3": "3",
        "\u06f4": "4",
        "\u06f5": "5",
        "\u06f6": "6",
        "\u06f7": "7",
        "\u06f8": "8",
        "\u06f9": "9",
    }
)


def contains_arabic(value: str) -> bool:
    return bool(ARABIC_RE.search(value))


def normalize_translation(value: str) -> str:
    value = value.translate(ARABIC_NORMALIZATION)
    return re.sub("[\u064b-\u065f\u0670\u06d6-\u06ed]", "", value)


def tracked_arabic_html() -> list[Path]:
    import subprocess

    result = subprocess.run(
        ["git", "ls-files", "articles/*.html"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    paths = [ROOT / line for line in result.stdout.splitlines() if line.strip()]
    return [
        path
        for path in paths
        if path.exists()
        and contains_arabic(path.read_text(encoding="utf-8", errors="replace"))
    ]


def load_cache() -> dict[str, str]:
    if not CACHE_PATH.exists():
        return {}
    try:
        data = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def save_cache(cache: dict[str, str]) -> None:
    CACHE_PATH.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def translated_response(response: requests.Response) -> str:
    response.raise_for_status()
    data = response.json()
    return "".join(part[0] for part in data[0] if part and part[0])


def request_translation(text: str) -> str:
    params = {
        "client": "gtx",
        "sl": "ar",
        "tl": "en",
        "dt": "t",
        "q": text,
    }
    last_error: Exception | None = None
    for attempt in range(5):
        try:
            response = requests.post(TRANSLATE_URL, data=params, timeout=45)
            return translated_response(response)
        except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
            last_error = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Translation request failed after retries: {last_error}")


def request_fallback_translation(text: str) -> str:
    chunks = split_long_text(text, limit=450)
    translated_chunks: list[str] = []
    for chunk in chunks:
        response = requests.get(
            FALLBACK_TRANSLATE_URL,
            params={"q": normalize_translation(chunk), "langpair": "ar|en"},
            timeout=45,
        )
        response.raise_for_status()
        result = response.json().get("responseData", {}).get("translatedText", "")
        if not result:
            raise RuntimeError("Fallback translation returned an empty response")
        translated_chunks.append(html.unescape(result).strip())
        time.sleep(0.2)
    translated = normalize_translation(" ".join(translated_chunks))
    if contains_arabic(translated):
        raise RuntimeError("Fallback translation still contains Arabic script")
    return translated


def split_long_text(text: str, limit: int = MAX_BATCH_CHARS) -> list[str]:
    if len(text) <= limit:
        return [text]
    sentences = re.split(r"(?<=[.!?؟])\s+", text)
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        if len(sentence) > limit:
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(
                sentence[index : index + limit]
                for index in range(0, len(sentence), limit)
            )
            continue
        candidate = f"{current} {sentence}".strip()
        if current and len(candidate) > limit:
            chunks.append(current)
            current = sentence
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks


def translate_batch(values: list[str]) -> dict[str, str]:
    payload_parts = [
        f"[[[AI_PROFIT_HUB_{index:04d}]]]\n{value}"
        for index, value in enumerate(values)
    ]
    translated = request_translation("\n".join(payload_parts))
    matches = list(MARKER_RE.finditer(translated))
    if len(matches) != len(values):
        raise RuntimeError(
            f"Translation marker mismatch: expected {len(values)}, found {len(matches)}"
        )
    result: dict[str, str] = {}
    for offset, match in enumerate(matches):
        start = match.end()
        end = matches[offset + 1].start() if offset + 1 < len(matches) else len(translated)
        result[values[int(match.group(1))]] = normalize_translation(
            translated[start:end].strip()
        )
    return result


def translate_values(values: list[str], cache: dict[str, str]) -> None:
    pending: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        if value in cache and contains_arabic(cache[value]):
            cache[value] = request_fallback_translation(value)
            save_cache(cache)
            continue
        if value in cache:
            continue
        if len(value) > MAX_BATCH_CHARS:
            translated_chunks = []
            for chunk in split_long_text(value):
                if chunk not in cache:
                    cache[chunk] = request_translation(chunk).strip()
                    save_cache(cache)
                translated_chunks.append(cache[chunk])
            cache[value] = " ".join(translated_chunks)
            save_cache(cache)
            continue
        pending.append(value)

    batch: list[str] = []
    batch_chars = 0
    for value in pending:
        marker_cost = 32
        if batch and batch_chars + len(value) + marker_cost > MAX_BATCH_CHARS:
            cache.update(translate_batch(batch))
            save_cache(cache)
            batch = []
            batch_chars = 0
            time.sleep(0.15)
        batch.append(value)
        batch_chars += len(value) + marker_cost
    if batch:
        cache.update(translate_batch(batch))
        save_cache(cache)


def core_text(value: str) -> str:
    return value.strip()


def collect_json_strings(value: Any, output: list[str]) -> None:
    if isinstance(value, str) and contains_arabic(value):
        output.append(value)
    elif isinstance(value, list):
        for item in value:
            collect_json_strings(item, output)
    elif isinstance(value, dict):
        for item in value.values():
            collect_json_strings(item, output)


def replace_json_strings(value: Any, cache: dict[str, str]) -> Any:
    if isinstance(value, str) and contains_arabic(value):
        return cache[value]
    if isinstance(value, list):
        return [replace_json_strings(item, cache) for item in value]
    if isinstance(value, dict):
        return {key: replace_json_strings(item, cache) for key, item in value.items()}
    return value


def prepare_page(path: Path) -> tuple[BeautifulSoup, list[str], list[tuple[Any, str]]]:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    values: list[str] = []
    json_nodes: list[tuple[Any, str]] = []

    for node in soup.find_all(string=True):
        parent = node.parent
        if isinstance(node, Comment):
            value = core_text(str(node))
            if value and contains_arabic(value):
                values.append(value)
            continue
        if parent and parent.name == "style":
            continue
        if parent and parent.name == "script":
            if (parent.get("type") or "").lower() == "application/ld+json":
                raw = str(node).strip()
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    value = core_text(str(node))
                    if value and contains_arabic(value):
                        values.append(value)
                else:
                    collect_json_strings(data, values)
                    json_nodes.append((node, raw))
            continue
        value = core_text(str(node))
        if value and contains_arabic(value):
            values.append(value)

    for tag in soup.find_all(True):
        for attr, raw_value in list(tag.attrs.items()):
            attr_values = raw_value if isinstance(raw_value, list) else [raw_value]
            for value in attr_values:
                if isinstance(value, str) and contains_arabic(value):
                    values.append(value)

    return soup, values, json_nodes


def apply_translation(
    soup: BeautifulSoup,
    cache: dict[str, str],
    json_nodes: list[tuple[Any, str]],
) -> str:
    del json_nodes
    for node in list(soup.find_all(string=True)):
        parent = node.parent
        if parent and parent.name == "style":
            continue
        if parent and parent.name == "script":
            raw = str(node).strip()
            if (parent.get("type") or "").lower() == "application/ld+json":
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    if contains_arabic(raw):
                        node.replace_with(NavigableString(cache[raw]))
                else:
                    replacement = json.dumps(
                        replace_json_strings(data, cache),
                        ensure_ascii=False,
                        indent=2,
                    )
                    node.replace_with(NavigableString(replacement))
            elif contains_arabic(raw):
                node.replace_with(NavigableString(cache[raw]))
            continue
        stripped = core_text(str(node))
        if stripped and contains_arabic(stripped):
            node.replace_with(str(node).replace(stripped, cache[stripped]))

    for tag in soup.find_all(True):
        for attr, raw_value in list(tag.attrs.items()):
            if isinstance(raw_value, list):
                tag.attrs[attr] = [
                    cache[value] if isinstance(value, str) and contains_arabic(value) else value
                    for value in raw_value
                ]
            elif isinstance(raw_value, str) and contains_arabic(raw_value):
                tag.attrs[attr] = cache[raw_value]

    return normalize_translation(str(soup))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Write translated HTML files")
    args = parser.parse_args()

    paths = tracked_arabic_html()
    print(f"Arabic HTML pages: {len(paths)}")
    if not args.apply:
        for path in paths:
            print(path.relative_to(ROOT).as_posix())
        return 0

    cache = load_cache()
    prepared: list[tuple[Path, BeautifulSoup, list[tuple[Any, str]]]] = []
    all_values: list[str] = []
    for path in paths:
        soup, values, json_nodes = prepare_page(path)
        prepared.append((path, soup, json_nodes))
        all_values.extend(values)

    translate_values(all_values, cache)
    for path, soup, json_nodes in prepared:
        translated = apply_translation(soup, cache, json_nodes)
        if contains_arabic(translated):
            raise RuntimeError(f"Arabic script remains after translation: {path}")
        path.write_text(translated + ("" if translated.endswith("\n") else "\n"), encoding="utf-8")
        print(f"Translated: {path.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
