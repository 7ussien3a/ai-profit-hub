#!/usr/bin/env python3
"""Replace isolated question-mark placeholders in known icon containers."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPLACEMENTS = (
    (
        re.compile(
            r'(<div\b[^>]*class=["\'][^"\']*\blogo-icon\b[^"\']*["\'][^>]*>)'
            r"\s*\?\s*(</div>)",
            re.IGNORECASE,
        ),
        r"\1&#9889;\2",
    ),
    (
        re.compile(
            r'(<button\b[^>]*\bid=["\']backToTop["\'][^>]*>)\s*\?\s*(</button>)',
            re.IGNORECASE,
        ),
        r"\1&#8593;\2",
    ),
    (
        re.compile(
            r'(<button\b[^>]*\bclass=["\'][^"\']*\bback-top\b[^"\']*["\'][^>]*>)'
            r"\s*\?\s*(</button>)",
            re.IGNORECASE,
        ),
        r"\1&#8593;\2",
    ),
    (
        re.compile(
            r'(<span\b[^>]*class=["\'][^"\']*\bq-opt-icon\b[^"\']*["\'][^>]*>)'
            r"\s*\?\s*(</span>)",
            re.IGNORECASE,
        ),
        r"\1&#10003;\2",
    ),
    (
        re.compile(
            r'(<div\b[^>]*class=["\'][^"\']*\btool-emoji\b[^"\']*["\'][^>]*>)'
            r"\s*\?\s*(</div>)",
            re.IGNORECASE,
        ),
        r"\1&#9881;\2",
    ),
    (
        re.compile(r"<span>\s*\?\s*</span>(\s*Formulate Your Request)", re.IGNORECASE),
        r'<span aria-hidden="true">&#9998;</span>\1',
    ),
    (
        re.compile(r'(<div\b[^>]*style=["\'][^"\']*font-size:2\.2rem[^"\']*["\'][^>]*>)'
                   r"\s*\?\s*(</div>)", re.IGNORECASE),
        r"\1AI\2",
    ),
)


def main() -> int:
    files_updated = 0
    replacements = 0
    for path in ROOT.rglob("*.html"):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        updated = text
        for pattern, replacement in REPLACEMENTS:
            updated, count = pattern.subn(replacement, updated)
            replacements += count
        if updated != text:
            path.write_text(updated, encoding="utf-8", newline="")
            files_updated += 1

    print(
        json.dumps(
            {
                "files_updated": files_updated,
                "icon_placeholders_repaired": replacements,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
