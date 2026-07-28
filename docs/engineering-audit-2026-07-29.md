# Engineering Audit and Production Hardening Notes

Date: 2026-07-29

## Executive Summary

AI Profit Hub is a static HTML, CSS, and JavaScript site deployed through Vercel from the GitHub `main` branch. The site has strong static rendering for article bodies, an existing sitemap and RSS feed, GA4, AdSense, legal pages, editorial pages, and a recently added Obsidian content workflow.

This pass focused on safe production hardening rather than a risky rebuild. The implementation added deployment security headers, deterministic related content, a reusable production audit script, cleanup for generated Markdown content state, and fixes for malformed image URLs that could affect structured data, social sharing, and visual rendering.

## Architecture Discovered

- Framework: custom static HTML, CSS, and JavaScript.
- Runtime: no production server runtime required for public pages.
- Build system: static files plus `scripts/content_pipeline.py` for Markdown-to-HTML content publishing.
- Routing: file-based static routes.
- Deployment: GitHub `main` to Vercel.
- Content sources: legacy hand-authored/generated HTML plus Markdown in `content/`.
- Search: `search.html`, `js/search-engine.js`, `data/tools.json`, `data/prompts.json`, and generated `data/search-index.json`.
- Related content: `js/related-articles.js` plus generated `data/related-content.json`.
- SEO: per-page metadata in HTML, `sitemap.xml`, `rss.xml`, `robots.txt`, and JSON-LD blocks.
- Analytics: GA4 measurement ID `G-8CSEDW0FVR`.
- Ads: AdSense publisher ID `ca-pub-4602905173099480`.

## Findings

### P0 Critical

- No tracked secrets were found by the audit script.
- Local secret-looking files exist but are not tracked: `credentials.json` and `scripts/service-account.json`.
- No malformed duplicated absolute URLs remain after this pass.

### P1 Important

- Many older article pages still lack complete title, description, or canonical metadata.
- Several older internal links point to routes that do not exist.
- Legacy Arabic public content remains in tracked files and requires a separate editorial migration if the site must be strictly English-only.
- Some older templates intentionally contain placeholder image tokens and should not be treated as production pages.

### P2 Improvements

- Related content was previously random and is now deterministic and context-aware.
- The content pipeline now removes stale generated Markdown pages from public outputs.
- A reusable site audit command now catches future regressions.

### P3 Future

- Full membership, payments, accounts, credits, and admin publishing should remain future work until authentication and server-side infrastructure are designed.

## Fixes Implemented

- Added Vercel security and cache headers in `vercel.json`.
- Added `/index.html` to `/` permanent redirect in `vercel.json`.
- Replaced malformed `https://ai-profit-hub.comhttps://...` URLs across tracked text files.
- Replaced repeated `..https://...` broken image references with valid `https://...` references.
- Fixed one broken homepage image reference by using an existing local image.
- Converted the Obsidian demo article from public `published` status to private review status.
- Updated the content pipeline to remove stale generated routes from `sitemap.xml` and `rss.xml`.
- Updated related-articles logic to rank recommendations by current page signals instead of random selection.
- Escaped related-card HTML output created from JSON-fed content.
- Added `scripts/site_audit.py` for XML, JSON, metadata, internal link, image, language, and tracked-secret checks.
- Added the site audit step to `publish-check`.

## Remaining Risks

- The site is not yet fully English-only because legacy tracked public pages contain Arabic script.
- Several older pages still need metadata and canonical remediation.
- Some older links need a content-aware redirect or replacement map.
- Full visual validation with browser screenshots was not completed in this pass.
- No JavaScript framework lint/type-check exists because the project is static JavaScript without a package toolchain.

## AdSense Readiness Classification

Classification: Needs improvement.

The site has the right foundation, legal pages, public content, and static rendering. Remaining approval risks are legacy non-English pages, older thin or duplicated pages, broken internal links, and incomplete metadata on older content.

## Commands

```powershell
python scripts/content_pipeline.py build
python scripts/site_audit.py
python scripts/content_pipeline.py publish-check
python -m unittest scripts.test_content_pipeline
```

## Next Phase

1. Create a redirect and replacement map for broken legacy internal links.
2. Batch-repair missing metadata and canonicals on older article pages after sampling template differences.
3. Decide whether to translate, archive, or noindex legacy Arabic pages.
4. Add browser-based visual screenshots for homepage, article, search, directory, comparison, review, contact, and 404 pages.
5. Expand content quality checks for thin pages and duplicate titles.
