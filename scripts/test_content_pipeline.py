import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import content_pipeline as pipeline


class ContentPipelineTests(unittest.TestCase):
    def test_reading_time_has_minimum_one(self):
        self.assertEqual(pipeline.reading_time("Short body."), 1)

    def test_slugify(self):
        self.assertEqual(pipeline.slugify("Hello, AI World!"), "hello-ai-world")

    def test_wikilink_resolution(self):
        item = pipeline.ContentItem(
            path=pipeline.ROOT / "content/articles/demo.md",
            meta={"title": "Demo Title", "slug": "demo-title", "contentType": "article", "status": "published"},
            body="",
        )
        pipeline.assign_public_url(item)
        lookup = pipeline.build_lookup([item])
        rendered = pipeline.resolve_wikilinks("[[Demo Title]]", lookup)
        self.assertEqual(rendered, "[Demo Title](/articles/demo-title.html)")

    def test_wikilink_to_draft_is_not_rendered_as_public(self):
        item = pipeline.ContentItem(
            path=pipeline.ROOT / "content/drafts/demo.md",
            meta={
                "title": "Draft Demo",
                "slug": "draft-demo",
                "contentType": "article",
                "status": "draft",
            },
            body="",
        )
        pipeline.assign_public_url(item)
        rendered = pipeline.resolve_wikilinks(
            "[[Draft Demo]]",
            pipeline.build_lookup([item]),
        )
        self.assertEqual(rendered, "Draft Demo")

    def test_draft_preview_uses_site_template_and_noindex(self):
        item = pipeline.ContentItem(
            path=pipeline.ROOT / "content/drafts/preview.md",
            meta={
                "title": "Draft Preview Article",
                "slug": "draft-preview-article",
                "description": "A complete description for testing a private draft preview with the production design.",
                "contentType": "article",
                "category": "Testing",
                "author": "Hussein Harby",
                "status": "draft",
                "updatedAt": "2026-07-30T00:00:00+03:00",
                "featuredImage": "/images/future-technology-abstract.jpg",
                "imageAlt": "Abstract technology preview image.",
                "canonical": "",
                "language": "en",
                "draft": True,
            },
            body="# Draft Preview Article\n\nThis is private preview content.",
        )
        pipeline.assign_public_url(item)
        rendered = pipeline.render_preview_html(item, [item])
        self.assertIn('<meta name="robots" content="noindex, nofollow">', rendered)
        self.assertIn("Draft Preview Article", rendered)
        self.assertIn("/css/", rendered)

    def test_noindex_status_is_supported(self):
        self.assertIn("noindex", pipeline.ALLOWED_STATUS)

    def test_frontmatter_parse(self):
        raw = "---\ntitle: \"Demo\"\ntags: [\"AI\", \"SEO\"]\nstatus: \"draft\"\n---\nBody"
        meta, body = pipeline.parse_frontmatter(raw, pipeline.ROOT / "demo.md")
        self.assertEqual(meta["title"], "Demo")
        self.assertEqual(meta["tags"], ["AI", "SEO"])
        self.assertEqual(body, "Body")

    def test_search_document_parser(self):
        parser = pipeline.SearchDocumentParser()
        parser.feed(
            """
            <html><head>
              <title>Fallback Title | AI Profit Hub</title>
              <meta name="description" content="A useful production description.">
              <meta property="og:image" content="/images/example.jpg">
              <meta http-equiv="refresh" content="0; url=/articles/example.html">
            </head><body>
              <nav>Navigation text</nav>
              <main><h1>Visible Article Title</h1><p>Searchable body text.</p></main>
              <script>ignored()</script>
            </body></html>
            """
        )
        self.assertEqual(" ".join(parser.h1_parts), "Visible Article Title")
        self.assertEqual(parser.meta["description"], "A useful production description.")
        self.assertIn("Searchable body text.", parser.body_parts)
        self.assertNotIn("Navigation text", parser.body_parts)
        self.assertTrue(parser.has_meta_refresh)


if __name__ == "__main__":
    unittest.main()
