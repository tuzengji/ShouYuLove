"""Regression tests for per-build loader reuse, with temporary pages and no real font."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import sys
import shutil
from unittest.mock import patch

from bs4 import BeautifulSoup
from PIL import Image


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
        template = ('<html><head><title>Test</title><link rel="icon" href="/old.ico"/>'
                    '<link rel="icon" href="/old.png"/><link rel="apple-touch-icon" href="/old-apple.png"/>'
                    '<link rel="manifest" href="/old.json"/></head><body><div id="__nuxt"></div>'
                    '<script id="__NUXT_DATA__" type="application/json">' +
                    json.dumps(payload) + '</script></body></html>')
        (self.builder.V0 / "index.html").write_text(template)
        fallback = self.builder.V0 / "projects/louis-vuitton-1/index.html"
        fallback.parent.mkdir(parents=True)
        fallback.write_text(template)
        self.content = dict(identity="Example", series="Series", dream="Dream", vision="Vision",
                            portfolio={"title":"Portfolio", "home":"Home"},
                            shortcut={"按钮": "Add", "关闭": "Close", "iPhone": "Share", "其他浏览器": "Menu", "内置浏览器": "Browser"},
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
                self.assertIsNone(soup.select_one('#syl-early'))
                self.assertNotIn('syl-fast-early', soup.html.get('class', []))
                self.assertEqual(loaders[0]['aria-valuenow'], '0')
                self.assertEqual(loaders[0]['aria-valuemax'], '100')
                self.assertNotIn('aria-hidden', soup.select_one('#__nuxt').attrs)
                self.assertEqual(len(soup.select('link[href="/assets/fonts.' + self.builder.MODULE_VERSION + '.css"]')), 1)
                self.assertFalse(soup.select('link[as="font"]'))
                for relation in ['icon', 'apple-touch-icon', 'manifest']:
                    links = soup.select(f'link[rel="{relation}"]')
                    self.assertEqual(len(links), 1)
                    self.assertIn(self.builder.BRAND_VERSION, links[0]['href'])

    def test_brand_assets_keep_install_identity_and_icon_sizes(self):
        name = Path('project-logos/20261012-主站-把爱递给你/shouyulove.svg')
        target = self.builder.ROOT / name
        target.parent.mkdir(parents=True)
        shutil.copy2(SOURCE.parents[1] / name, target)
        self.builder.brand_assets()
        folder = self.builder.OUT / self.builder.SHARED / 'shouyulove'
        for name, size in [('favicon', 64), ('apple-touch-icon', 180), ('home-icon-192', 192), ('home-icon-512', 512)]:
            with Image.open(folder / f'{name}.{self.builder.BRAND_VERSION}.png') as icon:
                self.assertEqual(icon.size, (size, size))
                self.assertEqual(icon.mode, 'RGBA' if name == 'favicon' else 'RGB')
                if name == 'favicon':
                    self.assertEqual(icon.getchannel('A').getextrema(), (0, 255))
        manifest = json.loads((folder / f'works-manifest.{self.builder.BRAND_VERSION}.json').read_text())
        self.assertEqual(manifest['id'], '/projects/')
        self.assertEqual(manifest['start_url'], '/portfolio/')
        self.assertEqual(manifest['scope'], '/portfolio/')
        self.assertEqual([icon['sizes'] for icon in manifest['icons']], ['192x192', '512x512'])
        for icon in manifest['icons']:
            self.assertTrue((self.builder.OUT / icon['src'].lstrip('/')).is_file())

    def test_project_ids_survive_insertions_and_reordering(self):
        text = (SOURCE.parents[1] / "content-source.md").read_text()
        projects = self.builder.parse_content(text)["projects"]
        self.assertEqual(len(projects), 10)
        by_id = {p["id"]: p for p in projects}
        self.assertEqual(by_id["signplay"]["url"], "https://shouyulove.cn/signplay/")
        self.assertEqual(by_id["signplay"]["designers"], "伍家阳")
        self.assertEqual(by_id["signplay"]["category"], "核心创意")
        self.assertEqual(by_id["pinhaoke"]["title"], "拼好课")
        self.assertEqual(by_id["jieguo"]["url"], "https://shouyulove.cn/catchpot/")
        festival = by_id["2026-sign-language-cultural-festival"]
        self.assertEqual(festival["designers"], "周丽敏 涂增基 黄庭逸")
        self.assertEqual(festival["category"], "核心创意")
        recap = by_id["2026-year-end-summary"]
        self.assertEqual(recap["url"], "https://shouyulove.cn/2026-year-end-summary/")
        self.assertEqual(recap["designers"], "涂增基 黄庭逸 潘婧欣 王宁静 叶子涵")
        misleading_label = text.replace("[进入 2026 手语分社骨干年终总结]", "[https://shouyulove.cn/2026-sign-language-cultural-festival/]")
        self.assertEqual(next(p for p in self.builder.parse_content(misleading_label)["projects"]
                              if p["id"] == recap["id"])["url"], recap["url"])
        import re
        pattern = r"(?m)^#### [^\n]+\n.*?(?=^#### |^### |\Z)"
        blocks = list(re.finditer(pattern, text, re.S))[:4]
        reordered = text[:blocks[0].start()] + ''.join(m.group() for m in reversed(blocks)) + text[blocks[-1].end():]
        self.assertEqual({p["id"]: p for p in self.builder.parse_content(reordered)["projects"]}, by_id)

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
