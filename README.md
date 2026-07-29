# AI Profit Hub

AI Profit Hub is a static publishing site for AI news, reviews, comparisons, guides, tools, companies, models, and prompts.

## Content Workflow

The editorial vault lives in `content/` and is ready to open directly in Obsidian. It uses only core Obsidian settings and local Markdown files.

Common commands:

```powershell
python scripts/content_pipeline.py audit
python scripts/content_pipeline.py validate
python scripts/content_pipeline.py build
python scripts/content_pipeline.py route-check
python scripts/site_audit.py
python scripts/content_pipeline.py preview --port 4173
python scripts/content_pipeline.py preview-draft "drafts/demo-ai-tool-review-draft.md" --port 4173
python tools/obsidian/mcp_server.py --self-test
.\scripts\publish-content.ps1
```

The build command renders published Markdown content to static HTML, then updates:

- `data/search-index.json`
- `data/related-content.json`
- `sitemap.xml`
- `rss.xml`

See `content/README.md` and `docs/obsidian-content-workflow.md` for the full schema, template, preview, and publishing workflow.

See `docs/engineering-audit-2026-07-29.md` for the latest production hardening audit notes.
