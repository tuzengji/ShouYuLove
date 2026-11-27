#!/usr/bin/env python3
"""Build the lightweight homepage and portfolio from the bound Markdown.

Each page is one HTML file with its styles, scripts and hand-drawn artwork inlined. Both
reuse what the site already serves: the first-paint font stylesheet, the square project
icons and, on the portfolio, the home-screen shortcut and click-tracking scripts.

    python3 -B scripts/build_home.py            # preview in output/home-preview/
    python3 -B serve.py --directory output/home-preview --port 8040
    python3 -B scripts/build_home.py --site     # write the site's own index.html and portfolio/index.html
                                                # and record them and their assets in the runtime manifests

Run it last: scripts/build_content.py still produces the older pages (/the-studio/, /projects/<id>/) and
would otherwise leave its own homepage and portfolio in place. With --site it also brings those older pages
in line (work pictures, site icons, categories and descriptions; see scripts/legacy_pages.py).
"""

import argparse
import ast
import colorsys
import functools
import hashlib
import io
import json
import math
import html
import re
import shutil
import string
from pathlib import Path

from bs4 import BeautifulSoup
from fontTools import subset
from PIL import Image
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

import icon_style
import legacy_pages
import sketch
from content_source import source_path

ROOT = Path(__file__).resolve().parents[1]
BUILD_CONTENT = ROOT / "scripts/build_content.py"
SHARED = "sites/immersive-g-com-955afd14/shared"
ASSETS = ROOT / SHARED / "assets"
HOME_ORDER = ["核心创意", "手语游戏", "心创组", "其他作品"]
SLUGS = {"核心创意": "core", "手语游戏": "games", "心创组": "internal", "其他作品": "secondary"}
MEMBERS_TITLE = "心创组第一届成员"
BRAND_MARK = ROOT / "project-logos/20261012-主站-把爱递给你/shouyulove.svg"
# Open-licensed typefaces (SIL OFL 1.1), kept outside Git in output/font-source/. Each is cut down to the pages'
# characters and to the one weight the design uses: (file, source, weight, Latin only).
# Headings are set in a Song face with real contrast, running text in a plain sans that stays crisp when small,
# and the Latin wordmark in an old-style italic.
FONT_SOURCE = ROOT / "output/font-source"
GOOGLE_FONTS = "https://github.com/google/fonts/raw/main/ofl/"
FONTS = {
    "SylSans": ("NotoSansSC[wght].ttf", GOOGLE_FONTS + "notosanssc/NotoSansSC%5Bwght%5D.ttf", 400, False),
    "SylSong": ("NotoSerifSC[wght].ttf", GOOGLE_FONTS + "notoserifsc/NotoSerifSC%5Bwght%5D.ttf", 600, False),
    "SylLatin": ("CormorantGaramond-Italic[wght].ttf", GOOGLE_FONTS + "cormorantgaramond/CormorantGaramond-Italic%5Bwght%5D.ttf", 500, True),
}
FONT_SLOT = "<!--fonts-->"
# Stickers pressed on by hand never sit quite straight.
# Each work's drawing sits on a scrap of cut paper instead of a grey app-icon square.
# The transparent masters live beside their sources; a work without an entry here uses the shared soft-colour set.
ICON_SETS = {
    "signplay": "20261015-signplay", "flyinghands": "20261020-flyinghands", "quna-study": "20261110-quna-study",
    "shouyu-pass": "20261113-shouyu-pass", "shouxiaoyu": "20261127-shouxiaoyu-avatar", "xinchuang-drive": "20261114-xinchuang-drive",
    "bombplane": "20261124-sign-games", "fruitbomb": "20261124-sign-games", "barbapapa": "20261124-sign-games",
    "codenames": "20261124-sign-games", "snowleopard": "20261124-sign-games", "skull": "20261125-skull",
    "perfectmenu": "20261125-perfectmenu", "naimahjong": "20261127-naimahjong-tile", "xiaoai-warm-cabin": "20261126-xiaoai-warm-cabin",
    "shouyu-shitingshuo": "20261127-shouyu-shitingshuo",
}
PAPERS = {"peach": "#f9dcc8", "butter": "#f8e7b0", "blush": "#f6d3d6", "mint": "#d3e8d8", "sky": "#d2e3f1", "lilac": "#e1d9ee"}
# Scissors never cut the same shape twice: (border-radius, turn, the shape it relaxes into under the pointer).
SCRAPS = [("58% 42% 55% 45% / 48% 56% 44% 52%", -8, "46% 54% 44% 56% / 56% 44% 54% 46%"),
          ("46% 54% 42% 58% / 55% 45% 55% 45%", 6, "56% 44% 54% 46% / 45% 56% 46% 54%"),
          ("52% 48% 60% 40% / 44% 52% 48% 56%", -3, "44% 56% 46% 54% / 54% 46% 56% 44%"),
          ("44% 56% 50% 50% / 56% 46% 54% 44%", 10, "55% 45% 45% 55% / 46% 55% 45% 54%")]
ICON_SIZE = 320
escape = html.escape


def shared_build():
    """Borrow the Markdown parser, shortcut markup and constants from build_content.py without importing it.

    Importing that module needs the archived Astra records, which this machine may not keep.
    """
    tree = ast.parse(BUILD_CONTENT.read_text(encoding="utf-8"))
    constants, functions = {}, []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in {"section", "parse_content", "home_shortcut"}:
            functions.append(node)
        elif isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name == "ENTRY_ICONS" or name.endswith("_VERSION"):
                try:
                    constants[name] = ast.literal_eval(node.value)
                except ValueError:
                    pass
    scope = {"re": re, "html": html, "BeautifulSoup": BeautifulSoup, "SOURCE": source_path(ROOT)}
    exec(compile(ast.Module(functions, []), str(BUILD_CONTENT), "exec"), scope)
    constants["home_shortcut"] = scope["home_shortcut"]
    return scope["parse_content"], constants


def brand_paths():
    """The hand-drawn hands and heart are traced from the approved mark's own outlines."""
    mark = BRAND_MARK.read_text(encoding="utf-8")
    group = re.search(r'<g transform="translate\(2 -11\)" stroke="#4b5d54" stroke-width="13"', mark)
    paths = re.findall(r'<path d="([^"]+)"', mark)
    assert group and len(paths) == 4, "The brand mark changed; review the hand-drawn hands."
    return dict(zip(["heart", "hand", "thumb", "cuff"], paths))


def hand(kind, slot):
    return f'<div class="hand hand--{kind}" aria-hidden="true">{sketch.hand_svg()}<i class="heart-slot" id="{slot}"></i></div>'


def heading(text, index, level="h2", extra=""):
    """A heading with one hand-drawn stroke under it."""
    return f'<{level}{extra}><span class="scribbled">{escape(text)}{sketch.underline(index)}</span></{level}>'


def phrases(text):
    """Wrap each sentence so a line break falls between sentences before it falls inside one."""
    return "".join(f'<span class="phrase">{escape(sentence)}</span>' for sentence in re.findall(r"[^。]+。?", text))


def characters(text):
    """One span per character, for the staggered rise of a headline."""
    return "".join(f'<span class="ch" style="--i:{index}"><span>{escape(char)}</span></span>' for index, char in enumerate(text))


def entry_icon(project, label, icons):
    assert (project, label) in icons, "Add an entry icon in build_content.ENTRY_ICONS for: " + label
    drawing = icon_style.tonal((ROOT / icons[(project, label)]).read_text(encoding="utf-8"))
    body = re.sub(r"<title[^>]*>.*?</title>", "", re.search(r"<svg[^>]*>(.*)</svg>", drawing, re.S).group(1), flags=re.S)
    return '<svg viewBox="0 0 256 256" aria-hidden="true">' + re.sub(r">\s+<", "><", body.strip()) + "</svg>"


def icon_original(project_id):
    """The icon as its designer drew it: a transparent PNG, with an SVG beside it when it is a vector drawing."""
    path = ROOT / "project-logos" / ICON_SETS.get(project_id, "20261012-柔和彩色") / (project_id + ".png")
    assert path.is_file(), f"Add the transparent icon for {project_id} (see ICON_SETS): {path}"
    return path


def icon_master(project_id):
    """What the pages show: the tonal redrawing of a vector icon, or the original picture when there is no vector."""
    original = icon_original(project_id)
    if not original.with_suffix(".svg").is_file():
        return original
    redrawn = ROOT / "project-logos" / icon_style.SET / original.name
    assert redrawn.is_file(), f"Run scripts/icon_style.py to redraw the icon for {project_id}"
    return redrawn


@functools.lru_cache(maxsize=None)
def icon_art(project_id):
    """The drawing alone, trimmed and centred on a transparent square: (address, WebP bytes, hue or None)."""
    mark = Image.open(icon_master(project_id)).convert("RGBA")
    bounds = mark.getchannel("A").point(lambda value: 255 if value >= 128 else 0).getbbox()
    assert bounds, project_id
    mark = mark.crop(bounds)
    scale = ICON_SIZE / max(mark.size)
    mark = mark.resize((round(mark.width * scale), round(mark.height * scale)), Image.Resampling.LANCZOS)
    picture = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    picture.paste(mark, ((ICON_SIZE - mark.width) // 2, (ICON_SIZE - mark.height) // 2), mark)
    data = io.BytesIO()
    picture.save(data, "WEBP", quality=92, method=6)
    # A drawing that is mostly one warm colour should not sit on warm paper, so note what it is made of.
    sample = mark.resize((48, 48)).tobytes()
    pixels = [colorsys.rgb_to_hsv(sample[i] / 255, sample[i + 1] / 255, sample[i + 2] / 255)
              for i in range(0, len(sample), 4) if sample[i + 3] > 200]
    vivid = [(hue, saturation) for hue, saturation, value in pixels if saturation > .18 and value > .35]
    hue = None
    if pixels and len(vivid) > len(pixels) / 2:
        hue = math.degrees(math.atan2(sum(math.sin(h * math.tau) * s for h, s in vivid),
                                      sum(math.cos(h * math.tau) * s for h, s in vivid))) % 360
    address = f"assets/next-icon-{project_id}.{hashlib.sha256(data.getvalue()).hexdigest()[:10]}.webp"
    return address, data.getvalue(), hue


def papers(projects):
    """One paper colour per work, the same on both pages: it suits the drawing and differs from its neighbours'."""
    chosen, used = {}, []
    for project in projects:
        hue = icon_art(project["id"])[2]
        if hue is not None and (hue < 75 or hue > 320):
            allowed = ["mint", "sky", "lilac"]
        elif hue is not None and hue < 100:
            allowed = ["blush", "lilac", "sky", "peach"]
        else:
            allowed = ["peach", "butter", "blush", "sky", "lilac"]
        if project["category"] == "手语游戏":  # these sit on the peach tray
            allowed = [name for name in allowed if name != "peach"]
        last = lambda name: max((index for index, other in enumerate(used) if other == name), default=-1)
        used.append(min(allowed, key=last))
        chosen[project["id"]] = PAPERS[used[-1]]
    return chosen


def tile(project, constants, paper, *, order=0, position=0, credit=True, tracked=False):
    """One work. With `tracked`, links carry the portfolio's click-tracking hooks."""
    shape, turn, relaxed = SCRAPS[(position + len(project["id"])) % len(SCRAPS)]
    icon = (f'<span class="tile-art" style="--paper-scrap:{paper};--shape:{shape};--shape-lit:{relaxed};--turn:{turn}deg">'
            f'<img class="tile-icon" src="/{icon_art(project["id"])[0]}" alt="" width="{ICON_SIZE}" height="{ICON_SIZE}" '
            f'loading="lazy" decoding="async"/>{sketch.pen_svg()}</span>')
    title = f'<h3 id="work-{project["id"]}"><span>{escape(project["title"])}</span></h3>'
    by = ('<p class="tile-by">设计者：' + " ".join(f"<span>{escape(name)}</span>" for name in project["designers"].split()) + "</p>") if credit else ""
    hook = f' data-project="{project["id"]}"' if tracked else ""
    style = f'style="--i:{order}"'
    opens = 'target="_blank" rel="noopener noreferrer"'
    if project["entries"]:
        # Several entries: the tile is a group and each entry is its own button.
        buttons = "".join(
            f'<a class="entry{" portfolio-link portfolio-action" if tracked else ""}"{hook} href="{escape(entry["url"], quote=True)}" {opens}>'
            f'{entry_icon(project["id"], entry["label"], constants["ENTRY_ICONS"])}<span>{escape(entry["label"])}</span></a>'
            for entry in project["entries"])
        return (f'<li><div class="tile pop{" portfolio-card" if tracked else ""}" {style} role="group" '
                f'aria-labelledby="work-{project["id"]}">{icon}<div>{title}<div class="entries">{buttons}</div>{by}</div></div></li>')
    return (f'<li><a class="tile pop{" portfolio-link" if tracked else ""}" {style}{hook} '
            f'href="{escape(project["url"], quote=True)}" {opens}>{icon}<div>{title}'
            f'<p class="tile-desc">{escape(project["description"])}</p>{by}</div></a></li>')


def head(title, description, canonical, constants, styles, extra=""):
    brand = {kind: "/" + address for kind, (address, _) in legacy_pages.brand().items()}
    css = "\n".join((ROOT / "styles" / name).read_text(encoding="utf-8") for name in styles) + extra
    assert "</style" not in css
    return "".join([
        '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"/>',
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"/>',
        f'<title>{escape(title)}</title><meta name="description" content="{escape(description, quote=True)}"/>',
        '<meta name="robots" content="index, follow"/><meta name="theme-color" content="#fffdfa"/>',
        '<meta name="format-detection" content="telephone=no"/>',
        '<meta name="apple-mobile-web-app-capable" content="yes"/><meta name="apple-mobile-web-app-title" content="以手予爱"/>',
        f'<link rel="canonical" href="{canonical}"/>',
        '<meta property="og:type" content="website"/><meta property="og:site_name" content="以手予爱 ShouYuLove"/>',
        f'<meta property="og:title" content="{escape(title, quote=True)}"/>',
        f'<meta property="og:description" content="{escape(description, quote=True)}"/>',
        f'<meta property="og:image" content="https://shouyulove.cn{brand["home-icon-512"]}"/>',
        f'<link rel="icon" type="image/png" sizes="64x64" href="{brand["favicon"]}"/>',
        f'<link rel="apple-touch-icon" sizes="180x180" href="{brand["apple-touch-icon"]}"/>',
        f'<link rel="manifest" href="{brand["works-manifest"]}"/>',
        FONT_SLOT,
        f'<style>{css}</style></head>'])


def scripts(*names):
    code = "\n".join((ROOT / "scripts" / name).read_text(encoding="utf-8") for name in names)
    assert "</script" not in code
    return f'<script>{code}</script>'


def home_works(content, constants):
    intro = {"核心创意": content["core"], "手语游戏": content["games"], "心创组": content["internal"], "其他作品": content["other"]}
    paper = papers(content["projects"])
    assert {project["category"] for project in content["projects"]} == set(HOME_ORDER), "Unknown category"

    # Every icon is the same size on both pages; a category only chooses how many columns it fills.
    def block(category, columns):
        tiles = "".join(tile(project, constants, paper[project["id"]], order=index % columns, position=index) for index, project in
                        enumerate(p for p in content["projects"] if p["category"] == category))
        count = sum(project["category"] == category for project in content["projects"])
        return (f'<header class="works-head rise"><div class="head-row">{heading(category, HOME_ORDER.index(category))}'
                f'<i class="head-rule" aria-hidden="true"></i><span class="head-count latin" aria-hidden="true">{count}</span></div>'
                f'<p>{escape(intro[category])}</p></header>'
                f'<ul class="tiles tiles--c{columns}">{tiles}</ul>')

    core, games, internal, other = HOME_ORDER
    return (f'<section class="works" id="works" data-stop><div class="wrap">{block(core, 3)}</div></section>'
            f'<section class="works tray tray--palm" data-stop><div class="wrap">{block(games, 4)}</div></section>'
            f'<section class="works" data-stop><div class="wrap">{block(internal, 3)}</div></section>'
            f'<section class="works" data-stop><div class="wrap">{block(other, 4)}</div></section>')


def home_page(content, constants):
    name = '以手予爱<span class="latin">ShouYuLove</span>'
    dream = "".join("<span>" + "".join(f"<i>{escape(char)}</i>" for char in sentence) + "</span>"
                    for sentence in re.findall(r"[^。]+。?", content["dream"]))
    bounds = "".join(f'<li class="rise" style="--i:{index}">{sketch.underline(index + 1)}{phrases(item)}</li>'
                     for index, item in enumerate(content["boundaries"]))
    members = "".join(f'<li class="rise" style="--i:{index}">{escape(member)}</li>' for index, member in enumerate(content["members"]))
    return "".join([
        head("以手予爱 ShouYuLove", content["identity"], "https://shouyulove.cn/", constants, ["next.css", "home.css"]),
        '<body id="top">', sketch.drawings(brand_paths()),
        '<section class="hero"><header class="mast wrap"><span>心创组</span>',
        f'<a href="/portfolio/">{escape(content["portfolio"]["title"])}</a></header>',
        '<div class="wrap hero-copy"><h1 aria-label="以手予爱 ShouYuLove">', characters("以手予爱"),
        f'<span class="latin">ShouYuLove</span></h1><p class="hero-id">{escape(content["identity"])}</p></div>',
        hand("give", "heart-from"), '</section>',
        '<main>',
        f'<section class="about" data-stop><div class="wrap"><p class="lead rise">{escape(content["series"])}</p>',
        f'<div class="pair pair--dream"><h2>梦想</h2><p class="dream" aria-label="{escape(content["dream"], quote=True)}">{dream}</p></div>',
        f'<div class="pair pair--vision rise"><h2>愿景</h2><p class="vision">{escape(content["vision"])}</p></div></div></section>',
        home_works(content, constants),
        f'<section class="bounds tray" data-stop><div class="wrap">{heading("边界", 2, extra=" class=\"rise\"")}<ul>{bounds}</ul></div></section>',
        f'<section class="members" data-stop><div class="wrap">{heading(MEMBERS_TITLE, 3, extra=" class=\"rise\"")}<ul>{members}</ul></div></section>',
        '</main>',
        '<footer class="finale"><div class="finale-inner">', hand("take", "heart-to"),
        f'<div class="wrap finale-copy"><p class="word">{name}</p>',
        f'<nav><a href="/portfolio/">{escape(content["portfolio"]["title"])}</a><a href="#top">回到顶部</a></nav></div></div>',
        f'<p class="wrap foot">{escape(content["identity"].removeprefix("我们是"))}</p></footer>',
        '<svg id="route" aria-hidden="true"><defs><clipPath id="route-walked"><rect x="0" y="0" width="0" height="0"/></clipPath></defs>',
        '<path class="route-ahead"/><path class="route-done" clip-path="url(#route-walked)"/></svg>',
        f'<div id="heart" aria-hidden="true"><div class="heart-in"><div class="heart-art">{sketch.heart_svg(rays=True)}</div></div></div>',
        f'<template id="spark">{sketch.heart_svg()}</template>',
        scripts("next.js", "home.js"), '</body></html>\n'])


def portfolio_page(content, constants):
    """The compact directory people add to their home screen; same order and credit rules as before."""
    labels = content["portfolio"]
    intro = {"核心创意": content["core"], "手语游戏": content["games"], "其他作品": content["other"], "心创组": content["internal"]}
    groups = [(category, [p for p in content["projects"] if p["category"] == category]) for category in labels["order"]]
    paper = papers(content["projects"])
    # The categories read like a table of contents: the name, how many works, and a hand-drawn line under the current one.
    chips = "".join(f'<li><a href="#portfolio-{SLUGS[category]}"><span>{escape(category)}</span>'
                    f'<sup class="latin">{len(projects)}</sup>{sketch.underline(index + 1)}</a></li>'
                    for index, (category, projects) in enumerate(groups))
    sections = []
    for number, (category, projects) in enumerate(groups):
        slug = SLUGS[category]
        tiles = "".join(tile(project, constants, paper[project["id"]], order=index % 3, position=index, tracked=True,
                             credit=category != "其他作品" or labels["show_other_designers"] or project["show_portfolio_credit"])
                        for index, project in enumerate(projects))
        title = heading(category, number, extra=f' id="portfolio-{slug}-title"')
        sections.append(
            f'<section class="portfolio-section portfolio-section--{slug}{" tray tray--palm" if slug == "games" else ""}" '
            f'id="portfolio-{slug}" aria-labelledby="portfolio-{slug}-title"><div class="wrap">'
            f'<header class="works-head rise"><div class="head-row">{title}<i class="head-rule" aria-hidden="true"></i>'
            f'<span class="head-count latin" aria-hidden="true">{len(projects)}</span></div><p>{escape(intro[category])}</p></header>'
            f'<ul class="tiles">{tiles}</ul></div></section>')
    shortcut = (ROOT / "styles/shouyulove-v1-1-jieguo.css").read_text(encoding="utf-8").split("/* Keep the works shortcut", 1)[1]
    thanks = f'<footer class="portfolio-thanks wrap"><small>{escape(labels["thanks"])}</small></footer>' if labels["thanks"] else ""
    return "".join([
        head(labels["title"] + " · 以手予爱 ShouYuLove", content["identity"], "https://shouyulove.cn/portfolio/", constants,
             ["next.css"], "\n/* Keep the works shortcut" + shortcut + (ROOT / "styles/works.css").read_text(encoding="utf-8")),
        '<body class="portfolio-page">', sketch.drawings(brand_paths()),
        '<header class="portfolio-header wrap"><div class="portfolio-bar">',
        f'<a href="/">{escape(labels["home"])}</a><span class="brand" aria-hidden="true">以手予爱<span class="latin">ShouYuLove</span></span></div>',
        f'<div class="portfolio-title"><div><h1 aria-label="{escape(labels["title"], quote=True)}">{characters(labels["title"])}</h1>',
        f'<p class="portfolio-id">{escape(content["identity"])}</p></div>',
        f'<button class="mascot" type="button" aria-label="爱心"><span class="heart-art">{sketch.heart_svg(rays=True)}</span></button></div></header>',
        f'<nav class="chips" aria-label="分类"><ul class="wrap">{chips}</ul></nav>',
        '<main id="portfolio">', "".join(sections), thanks, '</main>',
        str(constants["home_shortcut"](content)),
        f'<script defer src="/assets/home-shortcut.{constants["MODULE_VERSION"]}.js"></script>',
        f'<script defer src="/assets/portfolio-clicks.{constants["PORTFOLIO_CLICKS_VERSION"]}.js"></script>',
        scripts("next.js", "works.js"), '</body></html>\n'])


def font_file(family):
    name, address = FONTS[family][:2]
    path = FONT_SOURCE / name
    assert path.is_file(), f"Download {address} to {path} first."
    return path


def page_characters(document):
    """Everything a page can show, including copy that scripts read from attributes."""
    return set(html.unescape(re.sub(r"<(script|style)\b.*?</\1>", "", document, flags=re.S))) | set(string.printable) - set("\t\n\r\x0b\x0c")


def uncovered(document):
    """Every character on the page must exist in both Chinese typefaces, or a system font would show through."""
    missing = set()
    for family in ("SylSans", "SylSong"):
        glyphs = TTFont(font_file(family), lazy=True).getBestCmap()
        missing |= {char for char in page_characters(document) if ord(char) > 0x20 and ord(char) not in glyphs}
    return sorted(missing)


def typefaces(documents):
    """Cut each typeface to the pages' characters and its one weight.

    Returns the markup that loads them before first paint, and the addresses of the files it wrote.
    """
    characters = "".join(sorted(set().union(*(page_characters(document) for document in documents))))
    links, faces = [], []
    for family, (_, _, weight, latin_only) in FONTS.items():
        source = font_file(family)
        text = "".join(char for char in characters if ord(char) < 0x250) if latin_only else characters
        digest = hashlib.sha256(f"{text}{source.name}{source.stat().st_size}{weight}".encode()).hexdigest()[:10]
        address = f"assets/next-{family.lower()}.{digest}.woff2"
        target = ASSETS / address.removeprefix("assets/")
        if not target.exists():
            options = subset.Options(flavor="woff2", layout_features=["*"], notdef_outline=True)
            font = subset.load_font(str(source), options)
            subsetter = subset.Subsetter(options)
            subsetter.populate(text=text)
            subsetter.subset(font)
            # Subset first: pinning the weight of a full CJK variable font is slow, of a few hundred glyphs instant.
            font = instancer.instantiateVariableFont(font, {"wght": weight})
            target.parent.mkdir(parents=True, exist_ok=True)
            subset.save_font(font, str(target), options)
        links.append(f'<link rel="preload" as="font" type="font/woff2" href="/{address}" crossorigin/>')
        faces.append(f"@font-face{{font-family:{family};font-style:normal;font-weight:400;font-display:block;"
                     f"src:url(/{address}) format('woff2')}}")
    addresses = re.findall(r'href="/(assets/[^"]+)"', "".join(links))
    return "".join(links) + "<style>" + "".join(faces) + "</style>", addresses


def record(names):
    """Put the pages and their assets on the public whitelist. Nothing is taken off it: pages already open
    may still ask for the previous fonts and icons, which are immutable."""
    for manifest_name, wanted in (("runtime-manifest.json", names),
                                  ("origin-asset-manifest.json", [name for name in names if name.startswith(SHARED)])):
        path = ROOT / manifest_name
        manifest = json.loads(path.read_text(encoding="utf-8"))
        for name in wanted:
            data = (ROOT / name).read_bytes()
            manifest["files"][name] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        manifest["files"] = dict(sorted(manifest["files"].items()))
        manifest["bytes"] = sum(entry["bytes"] for entry in manifest["files"].values())
        path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f'{manifest_name}  {len(manifest["files"]):,} files  {manifest["bytes"]:,} bytes')


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    parser.add_argument("--out", type=Path, default=ROOT / "output/home-preview", help="preview directory")
    parser.add_argument("--site", action="store_true", help="write the site's own pages and update the runtime manifests")
    arguments = parser.parse_args()
    parse_content, constants = shared_build()
    content = parse_content()
    pages = {"index.html": home_page(content, constants), "portfolio/index.html": portfolio_page(content, constants)}
    for name, document in pages.items():
        missing = uncovered(document)
        assert not missing, f"{name} uses characters the typefaces lack: " + "".join(missing)
    # Fonts and icons are named by their content and live with the site's other versioned assets,
    # so the preview (which links to that directory) and the site serve the very same files.
    faces, assets = typefaces(pages.values())
    for project in content["projects"]:
        address, data, _ = icon_art(project["id"])
        (ASSETS / address.removeprefix("assets/")).write_bytes(data)
        assets.append(address)
    pages = {name: document.replace(FONT_SLOT, faces) for name, document in pages.items()}
    for address, data in legacy_pages.brand().values():
        legacy_pages.write(address, data)
    out = ROOT if arguments.site else arguments.out.resolve()
    if not arguments.site and (out / "portfolio").is_symlink():
        (out / "portfolio").unlink()
    for name, document in pages.items():
        (out / name).parent.mkdir(parents=True, exist_ok=True)
        (out / name).write_text(document, encoding="utf-8")
        print(f"{out / name}  {len(document.encode('utf-8')):,} bytes")
    print(f"{len(assets)} fonts and icons  {sum((ROOT / SHARED / address).stat().st_size for address in assets):,} bytes")
    if arguments.site:
        manifest = json.loads((ROOT / "runtime-manifest.json").read_text(encoding="utf-8"))
        paper = papers(content["projects"])
        scraps = {project["id"]: SCRAPS[(index + len(project["id"])) % len(SCRAPS)][:2]
                  for index, project in enumerate(content["projects"])}
        masters = {project["id"]: icon_master(project["id"]) for project in content["projects"]}
        older = legacy_pages.refresh(content, masters, paper, scraps, manifest["routes"], manifest["files"])
        print(f"{len(older)} files written or edited for the older pages")
        record([*pages, *(f"{SHARED}/{address}" for address in assets), *older])
        return
    shutil.copyfile(ROOT / "portfolio/projects.json", out / "portfolio/projects.json")
    for name, target in [("assets", ASSETS), ("sites", ROOT / "sites")]:
        link = out / name
        if not link.exists() and not link.is_symlink():
            link.symlink_to(target, target_is_directory=True)


if __name__ == "__main__":
    main()
