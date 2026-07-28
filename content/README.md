# AI Profit Hub Obsidian Vault

This folder is the Obsidian Vault for AI Profit Hub content.

Open this exact folder in Obsidian:

`site/content`

Do not open the full repository as the Vault. The full repository contains build scripts, public HTML, images, and Git data that should not be managed as writing notes.

## Folder Guide

- `articles/`: evergreen articles.
- `news/`: timely AI news.
- `reviews/`: product and model reviews.
- `comparisons/`: side-by-side comparisons.
- `guides/`: practical tutorials.
- `tools/`: AI tool pages.
- `companies/`: company profile pages.
- `models/`: AI model profile pages.
- `prompts/`: prompt pages.
- `drafts/`: unpublished working drafts.
- `templates/`: Obsidian templates.
- `assets/`: content images and attachments.
- `archive/`: retired notes that should not publish.

## Required Frontmatter for Published Content

Published content must include:

- `title`
- `slug`
- `description`
- `contentType`
- `category`
- `author`
- `status`
- `publishedAt`
- `updatedAt`
- `featuredImage`
- `imageAlt`
- `language`
- `sources`, when the content makes factual claims

Allowed status values:

- `draft`
- `review`
- `scheduled`
- `published`
- `archived`

## Internal Links

Use standard Markdown links when you know the URL:

```markdown
[Claude review](/articles/claude-opus-5-anthropic-review-july-2026.html)
```

Use Wiki Links while writing:

```markdown
[[Demo: Obsidian Content Workflow for AI Profit Hub]]
```

The build resolves Wiki Links to public URLs when it can match a title or slug.

## Images

Use existing production images from `/images/` when possible.

Use `assets/` for new drafting assets. Before publication, make sure every image has meaningful alt text.

## Preview

From the repository root, run:

```powershell
python scripts/content_pipeline.py build
python scripts/content_pipeline.py preview
```

The preview uses the same generated HTML, CSS, and layout as production.

## Publish

From the repository root, run:

```powershell
.\scripts\publish-content.ps1
```

This validates content, builds generated pages, updates search data, updates related content, updates the sitemap, updates RSS, and runs route checks.

The command does not push to Git automatically. Review the diff, commit, and push when ready.

## Rollback

To unpublish a Markdown item, change:

```yaml
status: "draft"
draft: true
```

Then run the publish command again.

To restore an older version, use Git:

```powershell
git log -- content articles data sitemap.xml rss.xml
git checkout <commit> -- <file>
```
