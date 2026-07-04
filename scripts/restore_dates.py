#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Profit Hub - Dates Restoration Script
=========================================
Extracts the original publication date of every article from the Git commit history
and updates the article HTML files and index.html to show genuine, honest dates.
"""

import os
import re
import datetime
import subprocess
from pathlib import Path

# Setup directories
SCRIPTS_DIR = Path(__file__).resolve().parent
SITE_DIR = SCRIPTS_DIR.parent
ARTICLES_DIR = SITE_DIR / 'articles'
INDEX_PATH = SITE_DIR / 'index.html'

def get_git_creation_date(file_rel_path):
    """Get YYYY-MM-DD from the first Git commit of the file."""
    try:
        # Run git log to find the first commit date
        res = subprocess.run(
            ['git', 'log', '--follow', '--diff-filter=A', '--format=%cs', '--', str(file_rel_path)],
            cwd=SITE_DIR,
            capture_output=True,
            text=True,
            check=True
        )
        date_str = res.stdout.strip().split('\n')[-1]
        if date_str and re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            return date_str
    except Exception as e:
        print(f"[WARN] Git check failed for {file_rel_path}: {e}")
    return None

def get_fallback_date(filename):
    """Extract YYYY-MM-DD from date suffix in filename if present, else today."""
    m = re.search(r'-(\d{4})(\d{2})(\d{2})(?:-\d{6})?\.html$', filename)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return "2026-07-04"

def format_human_date(date_str):
    """Convert YYYY-MM-DD to 'Month D, YYYY' (e.g. 'May 4, 2026')."""
    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    return dt.strftime("%B ") + str(dt.day) + dt.strftime(", %Y")

def update_article_file(filepath, true_date):
    """Update metadata, JSON-LD, and meta-bar date inside the article HTML."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update published_time meta tag
    # e.g., <meta property="article:published_time" content="2026-07-02T12:00:00+03:00">
    # or <meta property="article:published_time" content="2026-07-02">
    content = re.sub(
        r'(property="article:published_time"\s+content=")\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2})?(")',
        lambda m: m.group(1) + true_date + (m.group(2) if m.group(2) else "") + m.group(3),
        content
    )
    # Also modified_time (set same as published_time for legacy, or preserve if we want)
    content = re.sub(
        r'(property="article:modified_time"\s+content=")\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2})?(")',
        lambda m: m.group(1) + true_date + (m.group(2) if m.group(2) else "") + m.group(3),
        content
    )

    # 2. Update JSON-LD fields: "datePublished": "2026-07-02T12:00:00+03:00" or similar
    content = re.sub(
        r'("datePublished"\s*:\s*")\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2})?(")',
        lambda m: m.group(1) + true_date + (m.group(2) if m.group(2) else "") + m.group(3),
        content
    )
    content = re.sub(
        r'("dateModified"\s*:\s*")\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2})?(")',
        lambda m: m.group(1) + true_date + (m.group(2) if m.group(2) else "") + m.group(3),
        content
    )

    # 3. Update human-readable date in the meta-bar
    # We look for: <span>July 2, 2026</span> or 2026-07-02 inside the meta-bar
    human_date = format_human_date(true_date)
    
    # Let's replace any Month DD, YYYY inside <span> in the meta bar
    # Example: <span>July 2, 2026</span>
    # Wait, the meta bar dates are inside <span>...</span>
    # We can match Month DD, YYYY or YYYY-MM-DD inside <span> and replace with human_date
    months_pat = r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}'
    content = re.sub(
        rf'<span>({months_pat})</span>',
        f'<span>{human_date}</span>',
        content
    )
    content = re.sub(
        r'<span>\d{4}-\d{2}-\d{2}</span>',
        f'<span>{human_date}</span>',
        content
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def update_index_page(file_dates):
    """Parse and update all card dates in index.html to Month DD, YYYY format."""
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update news-grid cards:
    # Structure:
    # <a class="news-card" href="articles/..."> ... <span class="date">July 03, 2026</span>
    # We will find all news-card blocks
    def repl_news_card(m):
        href = m.group(1)
        filename = href.split('/')[-1]
        date_span = m.group(2)
        true_date = file_dates.get(filename)
        if true_date:
            human_date = format_human_date(true_date)
            return m.group(0).replace(date_span, f'<span class="date">{human_date}</span>')
        return m.group(0)

    # Match the news-card and extract its href and date span
    content = re.sub(
        r'<a class="news-card" href="articles/([^"]+)".*?(<span class="date">.*?</span>)',
        repl_news_card,
        content,
        flags=re.DOTALL
    )

    # 2. Update articles-grid cards:
    # Structure:
    # <article class="article-card ..."> ... <a href="articles/filename">...</a> ... <div class="article-card-meta"><span>DATE</span></div>
    # Let's find all article-card blocks
    # We can match from <article class="article-card to </article>
    def repl_article_card(m):
        card_content = m.group(0)
        href_match = re.search(r'href="articles/([^"]+)"', card_content)
        if href_match:
            filename = href_match.group(1)
            true_date = file_dates.get(filename)
            if true_date:
                human_date = format_human_date(true_date)
                # Find <div class="article-card-meta"><span>...</span></div>
                # or <span>2026-07-02</span>
                # Let's replace any <span>...</span> inside article-card-meta
                meta_match = re.search(r'(<div class="article-card-meta"><span>).*?(</span></div>)', card_content)
                if meta_match:
                    new_meta = meta_match.group(1) + human_date + meta_match.group(2)
                    card_content = card_content.replace(meta_match.group(0), new_meta)
                else:
                    # Fallback: find any <span>...</span> that matches date formats
                    months_pat = r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}'
                    card_content = re.sub(
                        rf'<span>({months_pat}|\d{4}-\d{2}-\d{2})</span>',
                        f'<span>{human_date}</span>',
                        card_content
                    )
        return card_content

    content = re.sub(
        r'<article class="article-card.*?".*?</article>',
        repl_article_card,
        content,
        flags=re.DOTALL
    )

    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    print("[OK] index.html card dates updated and standardized.")

def main():
    print("=" * 60)
    print("AI Profit Hub - Article & Index Dates Restoration")
    print("=" * 60)

    file_dates = {}
    
    # 1. Audit and retrieve true dates
    articles = sorted(ARTICLES_DIR.glob('*.html'))
    print(f"Auditing {len(articles)} article files...")
    
    for art_path in articles:
        filename = art_path.name
        rel_path = Path('articles') / filename
        
        # Try to get from Git first
        true_date = get_git_creation_date(rel_path)
        if not true_date:
            # Fallback to filename date suffix
            true_date = get_fallback_date(filename)
            print(f"  [FALLBACK] {filename} -> {true_date} (Not found in Git)")
        else:
            print(f"  [GIT] {filename} -> {true_date}")
            
        file_dates[filename] = true_date

    # 2. Update every article file
    print("\nUpdating article HTML files with true dates...")
    for art_path in articles:
        filename = art_path.name
        true_date = file_dates[filename]
        update_article_file(art_path, true_date)
        
    print("[OK] All article HTML files updated.")

    # 3. Update index.html
    print("\nUpdating index.html card dates...")
    update_index_page(file_dates)
    
    print("\nDone! Dates restoration successfully completed.")

if __name__ == '__main__':
    main()
