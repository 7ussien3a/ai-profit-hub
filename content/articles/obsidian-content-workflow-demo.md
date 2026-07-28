---
title: "Demo: Obsidian Content Workflow for AI Profit Hub"
slug: "obsidian-content-workflow-demo"
description: "A production-safe demo article proving that AI Profit Hub can publish English Markdown content from the Obsidian content workspace."
contentType: "article"
category: "Site Operations"
tags: ["Obsidian", "Content Workflow", "AI Profit Hub"]
author: "Hussein Harby"
editor: "AI Profit Hub Editorial"
status: "review"
publishedAt: "2026-07-29T00:00:00+03:00"
updatedAt: "2026-07-29T00:00:00+03:00"
featuredImage: "/images/future-technology-abstract.jpg"
imageAlt: "Abstract technology interface representing a structured publishing workflow."
canonical: "https://ai-profit-hub.com/articles/obsidian-content-workflow-demo.html"
keywords: ["Obsidian workflow", "AI Profit Hub content", "Markdown publishing"]
language: "en"
featured: false
draft: true
difficulty: "Beginner"
sources:
  - title: "Obsidian Help"
    url: "https://help.obsidian.md/"
related: ["qwen-38-max-vs-claude-opus-5-comparison-july-2026", "claude-opus-5-anthropic-review-july-2026"]
schemaType: "Article"
factChecked: true
lastReviewed: "2026-07-29"
testedBy: "AI Profit Hub content pipeline"
disclosure: "Demo content for validating the Obsidian publishing workflow."
---

# Demo: Obsidian Content Workflow for AI Profit Hub

This demo article is intentionally published to prove that AI Profit Hub can read Markdown content from the Obsidian workspace, validate frontmatter, render the article with the production website design, and update the public publishing assets.

It is not a news story and it does not make market claims. It is a controlled workflow sample for the site owner.

## Key Takeaways

- The article starts as a Markdown file inside the `content/` Obsidian Vault.
- The build pipeline calculates reading time automatically.
- The page keeps the public URL format used by existing articles.
- The generated HTML includes metadata, canonical tags, JSON-LD, RSS eligibility, and search index data.
- Internal links can use either Markdown links or Obsidian Wiki Links such as [[claude-opus-5-anthropic-review-july-2026]].

## How the Workflow Works

The owner writes content in Obsidian using a template. The Markdown file contains structured frontmatter at the top, followed by a normal article body. When the content is ready, the owner changes `status` from `draft` or `review` to `published`.

The local content pipeline then validates required fields, checks images, resolves internal links, generates HTML, updates the search index, updates related content, and appends eligible URLs to the sitemap and RSS feed.

## Practical Example

Use a standard Markdown link when you already know the public path:

```markdown
[Read the Claude review](/articles/claude-opus-5-anthropic-review-july-2026.html)
```

Use a Wiki Link when writing quickly inside Obsidian:

```markdown
[[claude-opus-5-anthropic-review-july-2026]]
```

During the build, the Wiki Link is resolved to the correct public article URL when a matching title or slug exists in the content index.

## Image Workflow

Images should live in `content/assets/` while drafting or in the existing public `images/` folder when they are already production assets. This demo uses an existing production image to avoid duplicating files.

Every published page requires `featuredImage` and `imageAlt`. Inline images also require meaningful alt text:

```markdown
![Workflow preview](/images/future-technology-abstract.jpg)
```

## Sources

- [Obsidian Help](https://help.obsidian.md/)

## FAQ

### Does this replace existing HTML articles?

No. Existing HTML articles remain in place. The Markdown pipeline is additive and safe for gradual migration.

### Can drafts appear on the public site?

No. Draft and archived content are excluded from generated pages, RSS, sitemap output, and search data.

### Can I keep old slugs?

Yes. The `slug` field controls the generated public filename, so a migrated article can preserve its existing URL.

### Does this require Obsidian community plugins?

No. The workflow uses Obsidian core features and repository scripts only.

## Related Content

- [[Qwen 3.8-Max vs. Claude Opus 5: The New Frontier of AI Efficiency (July 2026)]]
- [[claude-opus-5-anthropic-review-july-2026]]

## Hussein's Take

The safest CMS upgrade for this site is not a full rebuild. It is a controlled content layer that lets Obsidian handle writing while the existing static site keeps serving fast, crawlable HTML.

## Last Updated

Last updated: 2026-07-29.
