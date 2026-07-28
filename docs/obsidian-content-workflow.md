# Obsidian Content Workflow

## Overview

The `content/` folder is a local Obsidian vault for AI Profit Hub. Editors draft and review Markdown there, then the Python pipeline renders published entries into the existing static HTML site.

The implementation is intentionally light:

- No JavaScript framework was added.
- No production runtime dependency was added.
- No secrets or service credentials are required.
- The public site remains static and deployable through Vercel.

## Vault Structure

- `content/articles/` for evergreen articles and analysis.
- `content/news/` for time-sensitive news.
- `content/reviews/` for product and model reviews.
- `content/comparisons/` for versus articles.
- `content/guides/` for tutorials and practical guides.
- `content/tools/` for AI tool pages.
- `content/companies/` for company pages.
- `content/models/` for AI model pages.
- `content/prompts/` for prompt pages.
- `content/drafts/` for unpublished work.
- `content/templates/` for reusable Obsidian templates.
- `content/assets/` for draft-only assets.

## Status Flow

Use these frontmatter statuses:

- `draft`
- `review`
- `scheduled`
- `published`
- `archived`

Only `published` content is rendered to public HTML, search, sitemap, and RSS.

## Required Commands

Run validation while drafting:

```powershell
python scripts/content_pipeline.py validate
```

Build public output:

```powershell
python scripts/content_pipeline.py build
```

Preview locally with noindex headers:

```powershell
python scripts/content_pipeline.py preview --port 4173
```

Run the full publishing gate:

```powershell
.\scripts\publish-content.ps1
```

## Linking Rules

Markdown links and Wiki Links are both supported:

```markdown
[AI Profit Hub](https://ai-profit-hub.com)
[[obsidian-content-workflow-demo]]
[[obsidian-content-workflow-demo|Obsidian workflow demo]]
```

Wiki Links resolve against:

- Markdown titles.
- Markdown slugs.
- Markdown filenames.
- Existing HTML page titles.
- Existing HTML page filenames.

## Publishing Outputs

The pipeline writes published content to public routes based on `contentType`:

- `article`, `news`, and `model`: `articles/{slug}.html`
- `review`: `reviews/{slug}.html`
- `comparison`: `compare/{slug}.html`
- `guide`: `guides/{slug}.html`
- `company`: `companies/{slug}.html`
- `tool` and `prompt`: `articles/{slug}.html`

It also updates generated discovery files in `data/` so search and related content can include newly published Markdown pages.

## Quality Gate

Before publishing, confirm:

- Frontmatter matches `content/content.schema.json`.
- `language` is `en`.
- Required SEO fields are present.
- Featured images exist locally or use a valid absolute HTTPS URL.
- Sources are included for source-backed content.
- Wiki Links resolve.
- The build, route check, and XML checks pass.
