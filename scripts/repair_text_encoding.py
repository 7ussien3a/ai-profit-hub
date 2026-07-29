#!/usr/bin/env python3
"""Repair recurring replacement-character damage in legacy HTML files."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPLACEMENT = "\ufffd"


def repair_text(text: str) -> str:
    text = re.sub(
        r"([A-Za-z])\ufffd(s|t|re|ve|ll|d|m)\b",
        lambda match: f"{match.group(1)}\u2019{match.group(2)}",
        text,
    )
    text = re.sub(r"\ufffd\s+AI Profit Hub", "| AI Profit Hub", text)
    text = re.sub(r"</span>\s*\ufffd\s*<span", "</span> \u203a <span", text)
    text = text.replace("<span>\ufffd</span>", "<span>\u2022</span>")
    text = re.sub(r"\bth\ufffd(?=</span>)", "the\u2026", text)
    return text.replace(REPLACEMENT, "\u2014")


def tracked_html() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "*.html"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return [ROOT / line for line in result.stdout.splitlines() if line.strip()]


def main() -> int:
    changed = 0
    replacements = 0
    for path in tracked_html():
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        count = text.count(REPLACEMENT)
        if not count:
            continue
        repaired = repair_text(text)
        path.write_text(repaired, encoding="utf-8")
        changed += 1
        replacements += count
        print(f"Repaired {count}: {path.relative_to(ROOT).as_posix()}")
    print(f"Repaired {replacements} replacement characters across {changed} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
