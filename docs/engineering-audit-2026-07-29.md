# Engineering Audit and Production Hardening Notes

Date: 2026-07-29

## Executive Summary

AI Profit Hub is a static English-language HTML, CSS, and JavaScript site deployed to Vercel from the GitHub `main` branch. This engineering pass completed the legacy-language migration, consolidated duplicate articles, repaired internal routes and production metadata, strengthened the publishing audit, and validated representative public pages.

The final automated site audit reports zero errors and zero warnings. No P0 engineering blocker remains. AdSense approval cannot be guaranteed because approval is an external editorial decision, and machine-translated or generated legacy material still benefits from human fact-checking and source review.

## Architecture

- Framework: custom static HTML, CSS, and JavaScript.
- Runtime: no production server runtime is required for public pages.
- Build system: static files plus `scripts/content_pipeline.py` for Markdown publishing.
- Routing: file-based routes with permanent redirects in `vercel.json`.
- Deployment: GitHub `main` to Vercel.
- Search: a sitemap-backed JSON index with legacy inline data as a network-failure fallback.
- SEO: page metadata, JSON-LD, `sitemap.xml`, `rss.xml`, and `robots.txt`.
- Analytics: GA4 measurement ID `G-8CSEDW0FVR`.
- Ads: AdSense publisher ID `ca-pub-4602905173099480`.

## Baseline

- Audit errors: 0.
- Audit warnings: 211.
- Tracked files containing Arabic script: 97.
- Arabic-script matching lines: 3,833.
- Broken internal links: 45.
- Missing titles: 32.
- Missing descriptions: 66.
- Missing canonicals: 63.
- Broken image references: 2.

## Repairs Completed

- Translated 47 legacy HTML pages into English.
- Removed 47 redundant Markdown copies of those public HTML pages.
- Consolidated 15 duplicate article groups into descriptive canonical routes.
- Added 104 direct permanent redirects for legacy aliases and obsolete routes.
- Repaired 635 Unicode replacement characters across 59 HTML files.
- Converted two Windows-1252 pages to UTF-8.
- Repaired malformed internal links, image references, canonicals, Open Graph URLs, and JSON-LD URLs.
- Filled missing production metadata on affected public pages.
- Removed duplicate sitemap and RSS entries.
- Removed 55 redirect or `noindex` aliases from the sitemap while preserving their permanent redirects.
- Updated the publishing pipeline to prevent duplicate or non-indexable sitemap and RSS entries.
- Generated a 172-page production search index and a 146-page related-content index.
- Fixed the search page JavaScript parser failure and connected it to the generated index.
- Fixed an early DOM access error in the DeepSeek coding guide.
- Removed 114 obsolete template-instruction blocks, including 28 blocks that browsers could expose above article content.
- Restored 14 empty article hero images with matching local technical artwork.
- Repaired invalid social-image or structured-data image URLs on 18 affected pages.
- Marked authoring templates as `noindex, nofollow`.
- Regenerated `topics.json` with English content and repository-relative file paths.
- Added structured audit checks for tracked language, encoding, metadata, duplicate metadata, canonicals, JSON-LD, routes, redirects, images, sitemap, RSS, and tracked secret files.
- Added reusable repair utilities under `scripts/`.

## Credential Safety

- `credentials.json` and `scripts/service-account.json` remain ignored, untracked, and unchanged.
- No tracked credential file was found in reachable Git history.
- No stored private key, service-account payload, client secret, or hardcoded API-key assignment was detected in reachable Git history.
- One historical `GEMINI_API_KEY` environment-variable name appeared in a help message, not as a stored credential.
- No secret value was printed, rotated, deleted, or rewritten.

## Final Validation

- Final audit errors: 0.
- Final audit warnings: 0.
- Tracked Arabic-script matches: 0.
- Unicode replacement-character matches: 0.
- Broken internal route findings: 0.
- Broken image findings: 0.
- Duplicate sitemap routes: 0.
- Duplicate RSS routes: 0.
- Sitemap production URLs: 172.
- RSS production items: 73.
- Search-index entries: 172.
- Related-content entries: 146.
- JSON and XML parsing: passed.
- Content pipeline build: passed.
- Publishing checks: passed.
- Python unit tests: 5 passed.
- Python compile checks: passed.
- JavaScript syntax check: passed.
- Local HTTP smoke routes: 14 passed.
- Representative desktop browser routes: 11 passed without local request failures, JavaScript errors, broken images, or horizontal overflow.
- DeepSeek mobile article routes: 14 passed with visible headings and no broken images.
- Mobile DeepSeek article and Baidu homepage card: rendered correctly at 390 pixels with no blank overlay.

## Remaining Risks

### P0 Critical

None identified.

### P1 Important

- Human editorial review is still recommended for machine-translated legacy pages.
- Future-dated product, funding, policy, and market claims require source verification before being treated as factual reporting.
- The editorial heuristic report still flags 190 pages with 622 review items, mainly title or description length preferences, heading-count preferences, and missing external source links.
- AdSense may still reject content for editorial quality, originality, or policy reasons outside the scope of automated engineering checks.

### P2 Improvements

- Add a maintained browser regression suite for representative desktop and mobile routes.
- Add editorial source-age and citation-quality checks to the publishing workflow.

## AdSense Readiness

Classification: Needs improvement.

The site is technically deployable and no automated publishing blocker remains. The remaining approval risk is editorial rather than structural: translated and generated legacy articles should receive human accuracy, originality, and source-quality review. This classification should be upgraded only after that review, not solely because automated checks pass.

## Commands

```powershell
python scripts/content_pipeline.py build
python scripts/site_audit.py
python scripts/content_pipeline.py publish-check
python -m unittest scripts.test_content_pipeline
python -m compileall -q scripts audit_all.py extract_topics.py find_unprocessed.py
```
