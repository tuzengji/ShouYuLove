"""作品图标的套印画法（2026-11-27 用户从五种方案里选定，见 scripts/logo_options.py）。

像孔版印刷：线条一版、颜色一版，两版之间略微错位，色块里带油墨颗粒。图案仍是设计者的原稿：

- 线条版：每个形状用暖白填充（保留前后遮挡），描一条深墨绿细线；原稿的墨色小点保持墨色。
- 颜色版：原稿的颜色调得更鲜亮，不描边，整版向右下错开，以正片叠底印在线条版上，并带颗粒。
- 只有图片的图标（小爱、手小语、手语文化节、奶家麻将）不改原图，只在右下方垫一层同色系的错版底印。

错版叠色和颗粒要靠浏览器渲染，所以由本脚本用 Chromium（playwright）把每个作品画成 1024px 透明 PNG，
连同 SVG 存进 project-logos/<SET>/，build_home.py 只读这些 PNG，构建时不需要浏览器：

    python3 -B scripts/icon_riso.py

新增或修改作品图标后运行一次。入口按钮里的小图标由 build_home.py 直接内联 `entry()` 的结果。
"""

import base64
import colorsys
import hashlib
import io
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image

import icon_style
from icon_style import INK, SHAPES, SVG, brighten

ROOT = Path(__file__).resolve().parents[1]
SET = "20261127-套印"
PAPER = "#fffdfa"
INK_DEEP = "#1f352b"
SIZE = 1024
VIEW = "-10 -10 280 280"   # room for the colour plate that slips to the lower right
# Underprint inks for the picture icons, by hue.
UNDERPRINTS = {350: "#f4a6b8", 22: "#f6b48f", 45: "#f5d06f", 130: "#9fd6a9", 210: "#94bde8", 262: "#c3b0e8"}


def hls(colour):
    red, green, blue = (int(colour[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return colorsys.rgb_to_hls(red, green, blue)


def mix(colour, other, amount):
    a = [int(colour[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(other[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * amount):02x}" for x, y in zip(a, b))


def is_hex(colour):
    return re.fullmatch(r"#[0-9a-f]{6}", colour or "") is not None


def restyle(text, paint):
    """The drawing's shapes, where `paint(fill, stroke, width)` gives each its new (fill, stroke, width, extra attributes)."""
    root = ET.fromstring(text)

    def walk(node, inherited):
        own = dict(inherited)
        for key in ("fill", "stroke", "stroke-width"):
            if node.get(key) is not None:
                own[key] = node.get(key)
        kind = node.tag.split("}")[-1]
        if kind in SHAPES:
            fill = own.get("fill", "#000000").lower()
            stroke = own.get("stroke", "none").lower()
            width = float(own.get("stroke-width", "1") or 1)
            fill, stroke, width, extra = paint(fill, stroke, width)
            node.set("fill", fill)
            node.set("stroke", stroke)
            node.set("stroke-width", f"{width:.1f}")
            for key, value in extra.items():
                node.set(key, value)
        elif kind != "svg":
            for key in ("fill", "stroke", "stroke-width"):
                node.attrib.pop(key, None)
        for child in node:
            walk(child, own)

    walk(root, {})
    for title in root.findall(f"{{{SVG}}}title"):
        root.remove(title)
    return "".join(ET.tostring(child, encoding="unicode") for child in root)


def grain_filter(uid, frequency):
    """Ink that did not take: tiny gaps scattered through a colour plate."""
    return (f'<filter id="g{uid}" x="0" y="0" width="1" height="1">'
            f'<feTurbulence type="fractalNoise" baseFrequency="{frequency}" numOctaves="2" seed="7" result="n"/>'
            '<feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.5 1.5" result="m"/>'
            '<feComposite in="SourceGraphic" in2="m" operator="in"/></filter>')


def riso(text, uid, *, grain=.9, weight=.5, view="0 0 256 256", size=""):
    """A vector drawing printed as two plates: ink lines, and colour slipped to the lower right."""
    def line(fill, stroke, width):
        if fill == INK:
            return INK_DEEP, "none", 0, {}
        return (PAPER if is_hex(fill) else "none"), (INK_DEEP if stroke != "none" else "none"), min(width, 13) * weight, {}

    def colour(fill, stroke, width):
        if fill == INK:
            return "none", "none", 0, {}
        lively = lambda value: brighten(value, 1.9) if hls(value)[1] < .86 else mix(brighten(value, 1.9), "#f2b8a6", .35)
        if is_hex(fill):
            return lively(fill), "none", 0, {}
        if is_hex(stroke) and stroke != INK:
            return "none", lively(stroke), width * 1.4, {}
        return "none", "none", 0, {}
    body = (f'<g>{restyle(text, line)}</g>'
            f'<g transform="translate(10 8)" style="mix-blend-mode:multiply" filter="url(#g{uid})">{restyle(text, colour)}</g>')
    return f'<svg xmlns="{SVG}" viewBox="{view}"{size} aria-hidden="true"><defs>{grain_filter(uid, grain)}</defs>{body}</svg>'


def underprint(picture):
    """The riso ink closest to the picture's own colours."""
    sample = picture.convert("RGBA").resize((48, 48)).tobytes()
    vivid = []
    for i in range(0, len(sample), 4):
        if sample[i + 3] > 200:
            hue, saturation, value = colorsys.rgb_to_hsv(sample[i] / 255, sample[i + 1] / 255, sample[i + 2] / 255)
            if saturation > .2 and value > .35:
                vivid.append(hue * 360)
    hue = max(set(round(h / 30) * 30 % 360 for h in vivid), key=lambda h: sum(abs((x - h + 180) % 360 - 180) < 15 for x in vivid)) if vivid else 22
    return UNDERPRINTS[min(UNDERPRINTS, key=lambda key: abs((key - hue + 180) % 360 - 180))]


def picture_riso(path, uid, grain):
    """A picture icon left as it is, over a slipped plate of one riso ink in its silhouette."""
    picture = Image.open(path).convert("RGBA")
    data = io.BytesIO()
    picture.resize((512, 512), Image.Resampling.LANCZOS).save(data, "PNG")
    href = "data:image/png;base64," + base64.b64encode(data.getvalue()).decode()
    ink = underprint(picture)
    plate = (f'<filter id="u{uid}" x="0" y="0" width="1" height="1"><feFlood flood-color="{ink}"/>'
             '<feComposite in2="SourceAlpha" operator="in"/></filter>')
    image = f'<image href="{href}" x="0" y="0" width="256" height="256"/>'
    body = (f'<g transform="translate(10 8)" filter="url(#g{uid})"><g filter="url(#u{uid})">{image}</g></g>{image}')
    return f'<svg xmlns="{SVG}" viewBox="{VIEW}" aria-hidden="true"><defs>{grain_filter(uid, grain)}{plate}</defs>{body}</svg>'


def source(project_id):
    """The designer's vector drawing with this work's colour swaps (icon_style.RECOLOUR), or None for a picture icon."""
    import build_home
    path = build_home.icon_original(project_id).with_suffix(".svg")
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    for old, new in icon_style.RECOLOUR.get(project_id, {}).items():
        text = text.replace(old, new)
    return text


def drawing(project_id):
    """The SVG this script renders for one work."""
    import build_home
    text = source(project_id)
    if text is None:
        return picture_riso(build_home.icon_original(project_id), project_id, .5)
    return riso(text, project_id, grain=.5, weight=.42, view=VIEW)


def entry(path, key):
    """A small entry-button mark in the same print, with heavier lines so it survives at 30px."""
    uid = "e" + hashlib.sha256(key.encode()).hexdigest()[:8]
    return re.sub(r">\s+<", "><", riso(Path(path).read_text(encoding="utf-8"), uid, weight=.82).replace(f' xmlns="{SVG}"', ""))


def main():
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import build_home
    from playwright.sync_api import sync_playwright
    folder = ROOT / "project-logos" / SET
    folder.mkdir(exist_ok=True)
    projects = build_home.shared_build()[0]()["projects"]
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": SIZE, "height": SIZE})
        for project in projects:
            svg = drawing(project["id"])
            (folder / (project["id"] + ".svg")).write_text(svg + "\n", encoding="utf-8")
            page.set_content(f'<html><body style="margin:0;background:transparent">'
                             f'{svg.replace("<svg ", f"<svg width=\"{SIZE}\" height=\"{SIZE}\" ", 1)}</body></html>')
            page.wait_for_timeout(60)
            picture = Image.open(io.BytesIO(page.screenshot(omit_background=True, clip={"x": 0, "y": 0, "width": SIZE, "height": SIZE})))
            picture.save(folder / (project["id"] + ".png"), optimize=True)
            print("printed:", project["id"])
        browser.close()


if __name__ == "__main__":
    main()
