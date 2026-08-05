#!/usr/bin/env python3
"""
update_homepage.py — AI Profit Hub
====================================
Automatically updates the Latest Articles section in index.html
by reading the N most recent article HTML files and extracting
their metadata (title, description, image, tag, date).

Usage:
    python site/scripts/update_homepage.py          # updates index.html in-place
    python site/scripts/update_homepage.py --dry-run # prints diff only, no changes
    python site/scripts/update_homepage.py --count 9 # show top 9 articles (default: 6)

Run this after every publish cycle, before git push.
"""

import argparse
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]          # site/
ARTICLES_DIR = ROOT / "articles"
REVIEWS_DIR  = ROOT / "reviews"
COMPARE_DIR  = ROOT / "compare"
INDEX_HTML   = ROOT / "index.html"

# Marker comments that wrap the auto-generated block inside index.html
START_MARKER = "<!-- AUTO-ARTICLES:START -->"
END_MARKER   = "<!-- AUTO-ARTICLES:END -->"

# Default number of cards on the homepage
DEFAULT_COUNT = 6

# ── Helpers ────────────────────────────────────────────────────────────────
def _first(pattern: str, html: str, default: str = "") -> str:
    m = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip() if m else default


def extract_meta(html_path: Path) -> dict | None:
    """
    Extract card metadata from a published article HTML file.
    Returns None if the file should be skipped (noindex, draft, etc.).
    """
    try:
        text = html_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None

    # Skip pages explicitly marked noindex
    robots = _first(r'<meta\s+name="robots"\s+content="([^"]+)"', text)
    if "noindex" in robots.lower():
        return None

    # ── title ──
    title = _first(r'<meta\s+property="og:title"\s+content="([^"]+)"', text)
    if not title:
        title = _first(r'<title>([^<|]+)', text)
        title = re.sub(r'\s*\|\s*AI Profit Hub.*$', '', title).strip()
    if not title:
        return None

    # ── description ──
    desc = _first(r'<meta\s+name="description"\s+content="([^"]+)"', text)
    if not desc:
        desc = _first(r'<meta\s+property="og:description"\s+content="([^"]+)"', text)

    # ── image ──
    og_image = _first(r'<meta\s+property="og:image"\s+content="([^"]+)"', text)
    # Convert absolute URL → relative path for the card
    image = og_image.replace("https://ai-profit-hub.com", "")
    if not image:
        image = "/images/future-technology-abstract.jpg"

    # ── alt text ──
    alt = _first(r'<meta\s+name="description"\s+content="([^"]+)"', text)
    alt = title  # safe fallback

    # ── published date ──
    pub_iso = _first(r'<meta\s+property="article:published_time"\s+content="([^"]+)"', text)
    pub_display = ""
    if pub_iso:
        try:
            dt = datetime.fromisoformat(pub_iso.replace("Z", "+00:00"))
            pub_display = dt.strftime("%B %d, %Y")
        except ValueError:
            pub_display = pub_iso[:10]

    # ── tag ──
    # Try article-card-tag inside the page body first, else fall back to category from JSON-LD
    tag = _first(r'<span[^>]+class="article-card-tag"[^>]*>([^<]+)', text)
    if not tag:
        tag = _first(r'"articleSection"\s*:\s*"([^"]+)"', text)
    if not tag:
        tag = "AI News"

    # ── URL (relative to site root) ──
    rel_url = html_path.relative_to(ROOT).as_posix()   # e.g. articles/foo.html

    # ── sort key (epoch seconds) ──
    sort_key = 0
    if pub_iso:
        try:
            sort_key = int(
                datetime.fromisoformat(pub_iso.replace("Z", "+00:00"))
                .timestamp()
            )
        except ValueError:
            pass

    return {
        "title": title,
        "desc": desc,
        "image": image,
        "alt": alt,
        "tag": tag,
        "date": pub_display,
        "url": rel_url,
        "sort_key": sort_key,
    }


def collect_articles(n: int) -> list[dict]:
    """Scan articles/, reviews/, compare/ and return the N most recent."""
    dirs = [ARTICLES_DIR, REVIEWS_DIR, COMPARE_DIR]
    items = []
    for d in dirs:
        if not d.exists():
            continue
        for f in d.glob("*.html"):
            if f.name in {"index.html"}:
                continue
            meta = extract_meta(f)
            if meta:
                items.append(meta)

    items.sort(key=lambda x: x["sort_key"], reverse=True)
    return items[:n]


def build_card(m: dict, first: bool = False) -> str:
    """Render a single article card HTML string."""
    loading = 'eager" fetchpriority="high' if first else "lazy"
    # Truncate description to ~150 chars for cleaner cards
    excerpt = m["desc"]
    if len(excerpt) > 155:
        excerpt = excerpt[:152].rstrip() + "…"

    return f"""      <article class="article-card animate-in">
        <img src="{m['image']}" alt="{m['alt']}" class="article-card-image" loading="{loading}" decoding="async" width="800" height="450">
        <div class="article-card-body">
          <span class="article-card-tag">{m['tag']}</span>
          <h2 class="article-card-title"><a href="{m['url']}">{m['title']}</a></h2>
          <p class="article-card-excerpt">{excerpt}</p>
          <div class="article-card-meta">
            <span class="article-date">{m['date']}</span>
          </div>
        </div>
      </article>"""


def build_grid(articles: list[dict]) -> str:
    """Build the full articles-grid HTML block."""
    cards = "\n".join(
        build_card(a, first=(i == 0)) for i, a in enumerate(articles)
    )
    return (
        f"{START_MARKER}\n"
        f"    <div class=\"articles-grid\">\n"
        f"{cards}\n"
        f"    </div>\n"
        f"    {END_MARKER}"
    )


def update_index(articles: list[dict], dry_run: bool = False) -> bool:
    """
    Replace the AUTO-ARTICLES block in index.html.
    If the markers don't exist, inserts after the ad-space div.
    Returns True if any change was made.
    """
    original = INDEX_HTML.read_text(encoding="utf-8")
    new_grid = build_grid(articles)

    if START_MARKER in original and END_MARKER in original:
        updated = re.sub(
            re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
            new_grid,
            original,
            flags=re.DOTALL,
        )
    else:
        # First-time setup: replace the existing articles-grid div
        # Look for the pattern that starts the grid
        grid_pattern = re.compile(
            r'(<div class="articles-grid">.*?</div>\s*\n\s*)',
            re.DOTALL
        )
        if grid_pattern.search(original):
            updated = grid_pattern.sub(
                new_grid + "\n",
                original,
                count=1
            )
        else:
            # Fallback: insert after <!-- Ad Space (Top) --> block
            ad_block = '<!-- Ad Space (Top) -->'
            if ad_block in original:
                insert_after = original.index(ad_block)
                # Find next </div> after ad block
                close = original.index("</div>", insert_after) + 6
                updated = original[:close] + "\n\n    " + new_grid + original[close:]
            else:
                print("❌  Could not find insertion point in index.html. "
                      "Add markers manually:\n"
                      f"  {START_MARKER}\n  {END_MARKER}")
                return False

    if updated == original:
        print("ℹ️  index.html already up-to-date — no changes needed.")
        return False

    if dry_run:
        # Print a simple diff summary
        old_lines = original.splitlines()
        new_lines = updated.splitlines()
        removed = sum(1 for l in old_lines if l not in new_lines)
        added   = sum(1 for l in new_lines if l not in old_lines)
        print(f"[dry-run] Would change index.html: ~{removed} lines removed, ~{added} lines added.")
        return True

    INDEX_HTML.write_text(updated, encoding="utf-8")
    return True


def inject_markers_if_missing():
    """
    One-time helper: wraps the existing <div class="articles-grid"> block
    with AUTO-ARTICLES markers so future runs use the fast regex path.
    """
    text = INDEX_HTML.read_text(encoding="utf-8")
    if START_MARKER in text:
        return  # already done

    pattern = re.compile(
        r'(?P<before>[ \t]*)(?P<grid><div class="articles-grid">.*?</div>)(?P<after>\s)',
        re.DOTALL
    )
    m = pattern.search(text)
    if not m:
        print("⚠️  Could not auto-inject markers — wrap manually.")
        return

    replacement = (
        f"{m.group('before')}{START_MARKER}\n"
        f"{m.group('before')}{m.group('grid')}\n"
        f"{m.group('before')}{END_MARKER}{m.group('after')}"
    )
    updated = text[: m.start()] + replacement + text[m.end():]
    INDEX_HTML.write_text(updated, encoding="utf-8")
    print("✅  Markers injected into index.html for future auto-updates.")


# ── CLI ────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Auto-update AI Profit Hub homepage article cards."
    )
    parser.add_argument(
        "--count", "-n",
        type=int,
        default=DEFAULT_COUNT,
        help=f"Number of article cards to show (default: {DEFAULT_COUNT})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing to index.html",
    )
    parser.add_argument(
        "--inject-markers",
        action="store_true",
        help="One-time: add AUTO-ARTICLES markers to index.html",
    )
    args = parser.parse_args()

    if args.inject_markers:
        inject_markers_if_missing()
        return

    print(f"🔍  Scanning articles… (top {args.count})")
    articles = collect_articles(args.count)

    if not articles:
        print("❌  No publishable articles found.")
        sys.exit(1)

    print(f"📰  Found {len(articles)} articles to display:")
    for i, a in enumerate(articles, 1):
        print(f"    {i}. {a['date']}  {a['title'][:65]}")

    changed = update_index(articles, dry_run=args.dry_run)

    if changed and not args.dry_run:
        print(f"\n✅  index.html updated with {len(articles)} latest articles.")
        print("    Next step: git add index.html && git commit -m 'Update homepage cards' && git push")
    elif not changed:
        print("    Nothing to commit.")


if __name__ == "__main__":
    main()
