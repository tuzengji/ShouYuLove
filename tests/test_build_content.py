"""Regression tests for per-build loader reuse, with temporary pages and no real font."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import sys
from unittest.mock import patch

from bs4 import BeautifulSoup


SOURCE = Path(__file__).resolve().parents[1] / "scripts/build_content.py"


class LoaderBatchTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        source = root / "scripts/build_content.py"
        source.parent.mkdir()
        source.write_text(SOURCE.read_text())
        backup = root / "output/deployment/shouyulove-content-v1/v0-backup.json"
        backup.parent.mkdir(parents=True)
        backup.write_text(json.dumps({"local_backup": "/historical/V0-test"}))
        spec = importlib.util.spec_from_file_location("test_builder", source)
        self.builder = importlib.util.module_from_spec(spec)
        with patch('sys.path', [str(SOURCE.parent), *sys.path]):
            spec.loader.exec_module(self.builder)
        self.builder.OUT.mkdir(parents=True)
        shared = self.builder.OUT / self.builder.SHARED
        shared.mkdir(parents=True)
        self.builder.V0.mkdir(parents=True)
        payload = self.builder.flatten({
            "data": {"example": True},
            "pinia": {"ui": {"audio": {"isMuted": True}}, "datas": {}},
        })
        template = ('<html><head><title>Test</title></head><body><div id="__nuxt"></div>'
                    '<script id="__NUXT_DATA__" type="application/json">' +
                    json.dumps(payload) + '</script></body></html>')
        (self.builder.V0 / "index.html").write_text(template)
        fallback = self.builder.V0 / "projects/louis-vuitton-1/index.html"
        fallback.parent.mkdir(parents=True)
        fallback.write_text(template)
        self.content = dict(identity="Example", series="Series", dream="Dream", vision="Vision",
                            projects=[], boundaries=[], members=[])
        self.pages = {"" if i == 0 else f"page-{i}":
                      {"title": f"Page {i}", "url": "/" if i == 0 else f"/page-{i}/", "type": "home" if i == 0 else "project"}
                      for i in range(15)}

    def assert_all_loaders(self, expected):
        for route in self.pages:
            with self.subTest(route=route):
                soup = BeautifulSoup((self.builder.OUT / route / "index.html").read_text(), "html.parser")
                loaders = soup.select("#boot-loader")
                self.assertEqual(len(loaders), 1)
                self.assertEqual(loaders[0].select_one("svg path")["d"], expected)
                self.assertIsNone(loaders[0].find_parent(id="__nuxt"))
                self.assertIsNotNone(soup.select_one("#__nuxt noscript"))

    def test_font_refreshes_between_batches_and_every_page_keeps_loader(self):
        # A process running two builds must pick up a changed font, rather than a global cache.
        with patch.object(self.builder, "loader_wordmark", side_effect=[
            '<path d="M1 1"/>', '<path d="M2 2"/>',
        ]) as generate:
            self.builder.html_pages(self.content, self.pages, [], {})
            self.assertEqual(generate.call_count, 1)
            self.assert_all_loaders("M1 1")
            self.builder.html_pages(self.content, self.pages, [], {})
            self.assertEqual(generate.call_count, 2)
            self.assert_all_loaders("M2 2")

    def test_precomputed_runtime_wordmark_is_shared_with_all_html_pages(self):
        with patch.object(self.builder, "loader_wordmark", side_effect=AssertionError("font decoded twice")):
            self.builder.html_pages(self.content, self.pages, [], {}, '<path d="M3 3"/>')
        self.assert_all_loaders("M3 3")


if __name__ == "__main__":
    unittest.main()
