# AI Profit Hub Content Dashboard

Open `site/content` as the dedicated AI Profit Hub Obsidian Vault.

## Start Here

- [[README]]
- [[dashboards/Editorial Queues]]
- [[dashboards/Content Types]]
- [[research/Research Backlog]]
- [[sources/Source Index]]
- [[reports/GO Cycle Reports]]
- [[reports/Editorial Updates]]

## Editorial State

- Current drafts: [[drafts/demo-ai-tool-review-draft]]
- Under review: [[dashboards/Editorial Queues#Under Review]]
- Published Markdown content: [[articles/obsidian-content-workflow-demo]]
- Archived content: [[dashboards/Editorial Queues#Archived]]
- Noindex content: [[dashboards/Editorial Queues#Noindex]]
- Recently updated: [[dashboards/Editorial Queues#Recently Updated]]
- Source review required: [[dashboards/Editorial Queues#Source Review Required]]
- Editorial review required: [[dashboards/Editorial Queues#Editorial Review Required]]

## Content Types

- Articles: [[templates/standard-article]]
- News: [[templates/ai-news-article]]
- Reviews: [[templates/product-review]]
- Comparisons: [[templates/product-comparison]]
- Guides: [[templates/practical-guide]]
- Tools: [[templates/ai-tool-page]]
- Companies: [[templates/ai-company-page]]
- Models: [[templates/ai-model-page]]
- Prompts: [[templates/prompt-page]]

## Research

- Research backlog: [[research/Research Backlog]]
- United States: [[research/United States]]
- China: [[research/China]]
- Japan: [[research/Japan]]
- South Korea: [[research/South Korea]]
- Content clusters: [[research/Research Backlog#Cross-Country Opportunities]]
- Source notes: [[sources/Source Index]]

## Project Templates

- Source note: [[templates/source-note]]
- Research note: [[templates/research-note]]
- GO cycle report: [[templates/go-cycle-report]]
- Editorial update: [[templates/editorial-update-note]]

## Controlled Workflow

1. Create a note from a template.
2. Keep public-content candidates at `status: "draft"` while writing.
3. Add verified sources, local images, alt text, and internal links.
4. Run validation and a draft preview.
5. Move the note to `status: "review"` when it is editorially ready.
6. Use the standalone `GO` command for a complete research, publishing, Git, deployment, and production-verification cycle.

Saving an Obsidian note does not publish it. The Vault has no watcher, cron job, background publisher, Git plugin, or automatic deployment.

## Commands

Run from the repository root:

```powershell
python scripts/content_pipeline.py validate
python scripts/content_pipeline.py preview-draft "drafts/demo-ai-tool-review-draft.md" --port 4173
python tools/obsidian/mcp_server.py --self-test
```

The active content-operation prompt is linked from the repository documentation and is not duplicated in this Vault.
