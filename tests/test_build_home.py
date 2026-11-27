import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_home
import icon_style
import sketch


class NextPagesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        parse_content, cls.constants = build_home.shared_build()
        cls.content = parse_content((ROOT / "content-source.md").read_text(encoding="utf-8"))
        cls.home = build_home.home_page(cls.content, cls.constants)
        cls.portfolio = build_home.portfolio_page(cls.content, cls.constants)
        cls.addresses = [entry["url"] for project in cls.content["projects"] for entry in (project["entries"] or [project])]

    def links(self, document):
        return re.findall(r'<a class="(?:tile|entry)[^"]*"[^>]*? href="([^"]+)"', document)

    def test_every_project_keeps_its_approved_address(self):
        self.assertCountEqual(self.links(self.home), self.addresses)
        self.assertCountEqual(self.links(self.portfolio), self.addresses)

    def test_home_categories_follow_the_home_order(self):
        positions = [self.home.index(f'<span class="scribbled">{category}<') for category in build_home.HOME_ORDER]
        self.assertEqual(positions, sorted(positions))

    def test_portfolio_follows_the_source_order_and_credit_rules(self):
        positions = [self.portfolio.index(f'<span class="scribbled">{category}<') for category in self.content["portfolio"]["order"]]
        self.assertEqual(positions, sorted(positions))
        other = self.portfolio[self.portfolio.index('id="portfolio-secondary"'):]
        shown = [p for p in self.content["projects"] if p["category"] == "其他作品" and p["show_portfolio_credit"]]
        self.assertEqual(other.count("设计者："), len(shown))

    def test_portfolio_keeps_click_tracking_and_shortcut_hooks(self):
        tracked = re.findall(r'class="[^"]*portfolio-link[^"]*"[^>]*data-project="([^"]+)"', self.portfolio)
        self.assertEqual(len(tracked), len(self.addresses))
        self.assertEqual(set(tracked), {project["id"] for project in self.content["projects"]})
        for hook in ['<main id="portfolio">', 'id="syl-home-shortcut"', "/assets/home-shortcut.", "/assets/portfolio-clicks.",
                     'class="portfolio-header wrap"', '<a href="/">']:
            self.assertIn(hook, self.portfolio)

    def test_copy_comes_from_the_source(self):
        text = re.sub(r"<[^>]+>", "", re.sub(r"<(script|style)\b.*?</\1>", "", self.home, flags=re.S))
        for passage in [self.content["identity"], self.content["series"], self.content["dream"],
                        self.content["vision"], *self.content["boundaries"], *self.content["members"]]:
            self.assertIn(passage, text)

    def test_text_is_covered_by_the_body_typeface(self):
        if not (build_home.FONT_SOURCE / build_home.FONTS["SylSans"][0]).is_file():
            self.skipTest("font sources are kept outside Git")
        self.assertEqual(build_home.uncovered(self.home), [])
        self.assertEqual(build_home.uncovered(self.portfolio), [])

    def test_pages_are_flat_drawings_without_webgl(self):
        for document in (self.home, self.portfolio):
            self.assertNotIn("<canvas", document)
            self.assertNotIn("getContext", document)
        for slot in ['id="heart-from"', 'id="heart-to"', 'id="spark"']:
            self.assertIn(slot, self.home)

    def test_every_work_has_a_drawing_on_its_own_paper(self):
        paper = build_home.papers(self.content["projects"])
        for document in (self.home, self.portfolio):
            for project in self.content["projects"]:
                self.assertIn(f'--paper-scrap:{paper[project["id"]]}', document)
                self.assertIn(build_home.icon_art(project["id"])[0], document)
        for category in build_home.HOME_ORDER:
            row = [paper[p["id"]] for p in self.content["projects"] if p["category"] == category]
            self.assertTrue(all(left != right for left, right in zip(row, row[1:])), category)
        self.assertNotIn("-square.", self.home)

    def test_vector_icons_are_shown_in_their_tonal_redrawing(self):
        for project in self.content["projects"]:
            original = build_home.icon_original(project["id"]).with_suffix(".svg")
            shown = build_home.icon_master(project["id"])
            if not original.is_file():
                self.assertEqual(shown, build_home.icon_original(project["id"]))
                continue
            self.assertEqual(shown.parent.name, icon_style.SET)
            redrawn = shown.with_suffix(".svg").read_text(encoding="utf-8")
            self.assertEqual(redrawn, icon_style.tonal(original.read_text(encoding="utf-8")) + "\n", project["id"])
            self.assertNotIn(icon_style.INK, redrawn.lower())
        for document in (self.home, self.portfolio):
            for button in re.findall(r'<a class="entry.*?</a>', document, re.S):
                self.assertNotIn(icon_style.INK, button.lower())

    def test_drawings_are_reproducible_and_every_frame_is_referenced(self):
        paths = build_home.brand_paths()
        first = sketch.drawings(paths)
        self.assertEqual(first, sketch.drawings(paths))
        defined = set(re.findall(r'id="(sk-[a-z0-9-]+)"', first))
        used = set(re.findall(r'href="#(sk-[a-z0-9-]+)"', self.home))
        self.assertTrue(used <= defined, used - defined)
        self.assertEqual(defined, used)


if __name__ == "__main__":
    unittest.main()
