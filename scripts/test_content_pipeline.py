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
