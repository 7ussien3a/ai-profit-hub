# AI Profit Hub Obsidian Integration

## Verification Summary

- Initial classification: `PARTIALLY_CONNECTED`
- Repository result: `REPOSITORY_CONNECTED_CODEX_RESTART_REQUIRED`
- Verified on: `2026-07-30`
- Existing Vault architecture: reused and repaired
- Standalone MCP launcher and health: passed
- Native Codex loading: one Codex Desktop restart required
- Obsidian Desktop: installed; the AI Profit Hub Vault is registered separately
  and configured to open without replacing the existing unrelated Vault

The active unrelated Vault session was deliberately not closed for this
one-time setup. After Obsidian next reloads its Vault registry, open
`Dashboard.md` in the AI Profit Hub Vault.

## Verified Architecture

The dedicated AI Profit Hub Obsidian Vault is the repository-relative
`site/content` directory.

The existing `content/` source directory was selected because it already
contains the Markdown content model consumed by `scripts/content_pipeline.py`.
The repository root is not a Vault, and no duplicate content system exists.

The integration is independent from every other Vault and MCP server. Its
Codex MCP name is `ai-profit-hub-obsidian-local`; it does not share paths,
notes, templates, environment files, configuration, or tools with
`proterminal-obsidian-local`.

## Open the Vault

In Obsidian Desktop, open the exact `site/content` folder as a Vault. Start at
`Dashboard.md`. Do not open the repository root.

The committed core configuration:

- Creates new notes in `drafts/`.
- Stores attachments in `assets/`.
- Enables core Templates, Search, Backlinks, Outgoing Links, Outline, Tags,
  Properties, and Bookmarks.
- Disables Obsidian Publish and Sync.
- Uses no community plugins.

## Vault Structure

- `articles/`, `news/`, `reviews/`, `comparisons/`, `guides/`, `tools/`,
  `companies/`, `models/`, and `prompts/`: public-content candidates.
- `drafts/`: unpublished content candidates.
- `templates/`: content and project-note templates.
- `assets/`: controlled draft attachments.
- `sources/`: concise source notes.
- `research/`: research backlog and country indexes.
- `reports/`: GO cycle and editorial-update reports.
- `dashboards/`: maintained Markdown indexes.
- `archive/`: retired Markdown content.

`sources/`, `research/`, `reports/`, and `dashboards/` are editorial-only. The
publishing pipeline deliberately excludes them.

## Create a Draft

1. Open `Dashboard.md`.
2. Choose the template matching the content type.
3. Create the new note under the appropriate content folder or `drafts/`.
4. Keep `status: "draft"` and `draft: true` while writing.
5. Replace template placeholders with real metadata, sources, and local images.
6. Move the note to `status: "review"` when editorial review is appropriate.

Saving a note does not publish, commit, push, or deploy anything.

## Metadata and Statuses

Public-content frontmatter follows `content/content.schema.json`. Supported
statuses are:

- `draft`
- `review`
- `scheduled`
- `published`
- `archived`
- `noindex`

Only `status: "published"` with `draft: false` is rendered. Scheduled content
does not publish automatically. Draft, review, archived, and noindex content is
excluded from generated public pages and discovery files.

Source, research, GO report, and editorial-update templates follow
`content/editorial-note.schema.json`.

## Sources and Research

Create concise source notes with `templates/source-note.md`. Record the
official URL, publisher, country, publication date, access date, source type,
verification state, factual points, and original editorial analysis.

Do not copy complete source articles. Country research indexes are maintained
for the United States, China, Japan, and South Korea under `research/`.

## Images

- Use existing production images under `/images/` when possible.
- Store controlled draft attachments in `content/assets/`.
- Every content image requires meaningful English alt text.
- Published content must use local project paths.
- Do not hotlink external image-generation URLs.
- Do not move existing production images merely to satisfy Obsidian.

The pipeline checks featured and inline image paths. Obsidian's attachment
folder is fixed to `assets/`.

## Links

Normal Markdown links and Obsidian Wiki Links are supported:

```markdown
[AI Profit Hub](https://ai-profit-hub.com/)
[[articles/obsidian-content-workflow-demo]]
[[Demo: Obsidian Content Workflow for AI Profit Hub|Workflow example]]
```

The pipeline resolves Wiki Links by title, slug, filename, or Vault-relative
path. Published content fails validation for missing, ambiguous, or unpublished
Wiki Link targets. The renderer converts a valid public Wiki Link to the
corresponding website route.

## Validate

Run from the repository root:

```powershell
python scripts/content_pipeline.py validate
python tools/obsidian/mcp_server.py --self-test
python -m unittest scripts.test_content_pipeline scripts.test_obsidian_integration
```

Validation checks metadata, statuses, duplicate titles and slugs, dates,
language, Arabic script, local images, alt text, sources, canonicals, unsafe
HTML, Wiki Links, Vault configuration, and the fixed MCP boundary.

Draft placeholders may produce warnings. Critical issues block published
content.

## Preview a Draft

Run:

```powershell
python scripts/content_pipeline.py preview-draft "drafts/demo-ai-tool-review-draft.md" --port 4173
```

Open the printed localhost URL. The command renders the selected draft with the
production site template without writing a public HTML page or changing its
status. Preview responses and HTML are marked `noindex, nofollow`.

The existing full-site preview remains available:

```powershell
python scripts/content_pipeline.py preview --port 4173
```

## Publishing Preparation

The approved path remains:

Obsidian draft -> validation -> source review -> editorial review -> existing
generator -> local preview -> publish check -> site audit -> discovery-file
updates -> scoped Git commit -> push -> Vercel -> production verification.

The complete publishing gate is:

```powershell
python scripts/content_pipeline.py publish-check
```

The standalone `GO` command remains the only trigger for a complete research,
content-production, publishing, Git, deployment, and production-verification
cycle. The authoritative rules remain in
[`docs/agent/AI_PROFIT_HUB_MASTER_PROMPT.md`](agent/AI_PROFIT_HUB_MASTER_PROMPT.md).
They are not duplicated in the Vault.

## Archive and Noindex

- To retire Markdown content, use `status: "archived"` and move it to
  `archive/` when appropriate.
- Use `status: "noindex"` only after a documented page-level decision.
- Do not restore archived or noindex content without individual source and
  editorial review.
- Run the publishing gate during an authorised GO cycle to update generated
  discovery files.

## Resolve Validation Errors

Read the exact file and message printed by validation. Correct the source note,
frontmatter, Wiki Link, image, canonical, or content issue. Do not weaken the
validator to make an invalid page pass.

## Isolated Local MCP

The MCP launcher is `tools/obsidian/start-mcp.ps1`. The server:

- Computes the fixed Vault path from the AI Profit Hub repository.
- Accepts Markdown note operations only.
- Blocks path traversal, absolute paths, symlinks, hidden configuration,
  credentials, non-Markdown files, and other repositories.
- Provides health, path, list, read, create, update, search, Wiki Link, and
  validation tools.
- Provides no delete, publish, shell, scheduling, or background capability.

Standalone health:

```powershell
python tools/obsidian/mcp_server.py --self-test
```

After first registration in the Codex user configuration, restart Codex
Desktop once. Do not claim native loading until tools with the
`ai-profit-hub-obsidian-local` namespace are visible.

## Credential Protection

`credentials.json` and `scripts/service-account.json` stay outside the Vault,
ignored, untracked, unchanged, absent from build output, and unreachable
through the MCP server. The server cannot be redirected to another Vault.
