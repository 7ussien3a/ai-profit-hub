# AI Profit Hub Content Dashboard

Open this folder as the Obsidian Vault:

`content/`

## Start Here

- [[README]]
- [[templates/standard-article]]
- [[templates/ai-news-article]]
- [[articles/obsidian-content-workflow-demo]]
- [[drafts/demo-ai-tool-review-draft]]

## Editorial Queues

### Drafts

- [[drafts/demo-ai-tool-review-draft]]

### Published Markdown Content

- [[articles/obsidian-content-workflow-demo]]

### Review Queue

No review items yet. Set `status: "review"` in frontmatter when an article needs editorial review.

### Scheduled Content

No scheduled items yet. Set `status: "scheduled"` and a future `publishedAt` value when scheduling becomes needed.

### Content Missing Images

Run:

```powershell
python scripts/content_pipeline.py validate
```

### Content Missing Sources

Run:

```powershell
python scripts/content_pipeline.py validate
```

### Outdated Content

Run:

```powershell
python scripts/content_pipeline.py report
```

## Content Types

- Articles: `articles/`
- News: `news/`
- Reviews: `reviews/`
- Comparisons: `comparisons/`
- Guides: `guides/`
- Tools: `tools/`
- Companies: `companies/`
- Models: `models/`
- Prompts: `prompts/`
- Drafts: `drafts/`
- Archived content: `archive/`

## Daily Workflow

1. Create a note from a template.
2. Keep `status: "draft"` while writing.
3. Add sources, image alt text, and internal links.
4. Run validation and preview.
5. Change `status` to `published`.
6. Run the publish command.
