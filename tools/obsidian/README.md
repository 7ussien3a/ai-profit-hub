# AI Profit Hub Obsidian MCP

This directory contains the isolated local MCP server for the AI Profit Hub
Obsidian Vault.

## Boundary

- Server name: `ai-profit-hub-obsidian-local`
- Fixed Vault: `site/content`
- Allowed files: Markdown notes inside that Vault
- Excluded: `.obsidian`, `.trash`, Git data, credentials, non-Markdown files,
  other repositories, and other Obsidian Vaults
- Publishing capability: none
- Scheduling capability: none
- Delete capability: none

The server computes the Vault path from its own repository location. It does
not accept an environment variable that can redirect it to ProTerminal or
another project.

## Standalone Health Check

From the repository root:

```powershell
python tools/obsidian/mcp_server.py --self-test
```

The test verifies Vault health and blocks path traversal. The complete
integration test also creates and removes a dedicated draft fixture.

## Codex Registration

The user-level Codex configuration contains a separate
`[mcp_servers.ai-profit-hub-obsidian-local]` entry. It does not replace or
modify `proterminal-obsidian-local`.

After the entry is first added, restart Codex Desktop once and verify that the
`ai-profit-hub-obsidian-local` tools are visible before claiming native MCP
loading.
