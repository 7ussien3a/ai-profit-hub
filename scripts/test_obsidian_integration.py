import json
import unittest
from pathlib import Path

from tools.obsidian import mcp_server


FIXTURE_PATH = "drafts/codex-obsidian-integration-test.md"
FIXTURE = """---
title: "Codex Obsidian Integration Test"
slug: "codex-obsidian-integration-test"
description: "A temporary English draft used only to verify the isolated Obsidian integration safely."
contentType: "article"
category: "Testing"
tags: ["Test"]
author: "Hussein Harby"
status: "draft"
publishedAt: ""
updatedAt: "2026-07-30T00:00:00+03:00"
featuredImage: "/images/future-technology-abstract.jpg"
imageAlt: "Abstract technology integration test image."
canonical: ""
language: "en"
featured: false
draft: true
sources: []
related: ["obsidian-content-workflow-demo"]
schemaType: "Article"
factChecked: false
lastReviewed: ""
disclosure: "Temporary local integration test."
---

# Codex Obsidian Integration Test

This fixture verifies safe reading, writing, search, validation, and Wiki Link
resolution. It is never published.

Related workflow: [[Demo: Obsidian Content Workflow for AI Profit Hub]]
"""


class ObsidianIntegrationTests(unittest.TestCase):
    def tearDown(self):
        path = mcp_server.resolve_note_path(FIXTURE_PATH)
        path.unlink(missing_ok=True)

    def test_fixed_vault_and_path_isolation(self):
        expected = (mcp_server.ROOT / "content").resolve()
        self.assertEqual(mcp_server.VAULT, expected)
        with self.assertRaises(mcp_server.VaultError):
            mcp_server.resolve_note_path("../../credentials.json")
        with self.assertRaises(mcp_server.VaultError):
            mcp_server.resolve_note_path("credentials.json")
        with self.assertRaises(mcp_server.VaultError):
            mcp_server.resolve_note_path(
                "C:/Users/Admin/Desktop/X/ProTerminal/content/private.md"
            )

    def test_read_write_search_update_and_links(self):
        created = mcp_server.create_note(FIXTURE_PATH, FIXTURE)
        self.assertEqual(created["created"], FIXTURE_PATH)
        listed = mcp_server.list_notes("drafts")
        self.assertIn(FIXTURE_PATH, [note["path"] for note in listed["notes"]])
        read = mcp_server.read_note(FIXTURE_PATH)
        self.assertEqual(read["frontmatter"]["status"], "draft")
        found = mcp_server.search_notes("temporary English draft", "drafts")
        self.assertEqual(found["count"], 1)
        updated_content = FIXTURE.replace(
            "It is never published.",
            "It remains excluded from every public discovery file.",
        )
        updated = mcp_server.update_note(FIXTURE_PATH, updated_content)
        self.assertEqual(updated["updated"], FIXTURE_PATH)
        links = mcp_server.resolve_links(FIXTURE_PATH)
        self.assertTrue(links["valid"])
        self.assertEqual(links["links"][0]["status"], "resolved")
        validation = mcp_server.validate_vault()
        self.assertEqual(validation["status"], "PASS", validation["issues"])

    def test_templates_and_obsidian_core_configuration(self):
        app = json.loads(
            (mcp_server.VAULT / ".obsidian" / "app.json").read_text(encoding="utf-8")
        )
        templates = json.loads(
            (mcp_server.VAULT / ".obsidian" / "templates.json").read_text(
                encoding="utf-8"
            )
        )
        community = json.loads(
            (mcp_server.VAULT / ".obsidian" / "community-plugins.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(app["attachmentFolderPath"], "assets")
        self.assertEqual(app["newFileFolderPath"], "drafts")
        self.assertEqual(templates["folder"], "templates")
        self.assertEqual(community, [])
        required = {
            "standard-article.md",
            "ai-news-article.md",
            "product-review.md",
            "product-comparison.md",
            "practical-guide.md",
            "ai-tool-page.md",
            "ai-company-page.md",
            "ai-model-page.md",
            "source-note.md",
            "research-note.md",
            "go-cycle-report.md",
            "editorial-update-note.md",
        }
        existing = {path.name for path in (mcp_server.VAULT / "templates").glob("*.md")}
        self.assertTrue(required.issubset(existing))

    def test_mcp_protocol_and_health(self):
        initialised = mcp_server.handle(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {"protocolVersion": "2024-11-05"},
            }
        )
        self.assertEqual(
            initialised["result"]["serverInfo"]["name"],
            "ai-profit-hub-obsidian-local",
        )
        tools = mcp_server.handle(
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
        )
        self.assertEqual(len(tools["result"]["tools"]), 9)
        health = mcp_server.health_check()
        self.assertEqual(health["status"], "PASS", health["issues"])


if __name__ == "__main__":
    unittest.main()
