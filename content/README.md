# AI Profit Hub Obsidian Vault

Open the repository-relative `site/content` folder in Obsidian.

Do not open the repository root. Start with [[Dashboard]].

## Working Areas

- Public-content candidates: `articles/`, `news/`, `reviews/`,
  `comparisons/`, `guides/`, `tools/`, `companies/`, `models/`, and
  `prompts/`.
- Unpublished candidates: `drafts/`.
- Templates: `templates/`.
- Draft attachments: `assets/`.
- Editorial-only work: `sources/`, `research/`, `reports/`, and `dashboards/`.
- Retired Markdown content: `archive/`.

Editorial-only folders never enter the public content generator.

## Safe Draft Workflow

1. Create a note from the appropriate template.
2. Keep `status: "draft"` and `draft: true`.
3. Replace all placeholder metadata.
4. Add verified sources, local image paths, alt text, and working links.
5. Validate and preview.
6. Use `status: "review"` when the draft is ready for editorial review.

Saving a note never publishes it. The standalone `GO` command remains the only
trigger for a complete publishing and deployment cycle.

## Statuses

- `draft`
- `review`
- `scheduled`
- `published`
- `archived`
- `noindex`

Only `published` content with `draft: false` is rendered. `scheduled` does not
create automatic publishing.

## Links

Normal Markdown links and Wiki Links are supported:

```markdown
[Claude review](/articles/claude-opus-5-anthropic-review-july-2026.html)
[[articles/obsidian-content-workflow-demo]]
```

Published notes fail validation when a Wiki Link is missing, ambiguous, or
points to unpublished Vault content.

## Images

Use local production paths under `/images/` where possible. Obsidian
attachments go to `assets/`. Published images require meaningful English alt
text and cannot use external generation URLs.

## Commands

Run from the repository root:

```powershell
python scripts/content_pipeline.py validate
python scripts/content_pipeline.py preview-draft "drafts/demo-ai-tool-review-draft.md" --port 4173
python tools/obsidian/mcp_server.py --self-test
python scripts/content_pipeline.py publish-check
```

`publish-check` prepares production output but does not commit or push. Use it
only inside an authorised workflow, review the scoped Git diff, then commit and
push when approved by the active GO rules.

See `docs/obsidian-content-workflow.md` for complete setup, validation, MCP,
preview, source, image, archive, and security details.
