"""作品图标的五种重画方案，供用户挑选。

每种方案都从设计者的矢量原稿（project-logos/ 里的 SVG）自动生成，图案本身不变，只换画法：

1. 墨线：深墨绿细线勾勒，留白为主，只有爱心一类的粉色部分点一笔豆沙色。
2. 套印：像孔版印刷，颜色一版、线条一版，两版之间略微错位，色块带油墨颗粒。
3. 印章：图案以留白反刻在一方深色印章里，边缘带一点钤印的毛边。
4. 彩铅：浅色打底，再用同色彩铅斜向排线，轮廓是略带抖动的深一号线条，和首屏插画同一种手法。
5. 剪纸：不描边，每块颜色是一张纸片，叠在下面的纸片上投出一小块实色阴影。

    python3 -B scripts/logo_options.py

输出 output/home-preview/logo-options/index.html（预览服务 serve.py 下打开 /logo-options/）。
"""

import colorsys
import copy
import io
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import legacy_pages  # noqa: F401,E402  (sets up cairosvg on macOS)
import cairosvg  # noqa: E402
from PIL import Image  # noqa: E402

import build_home  # noqa: E402
import icon_style  # noqa: E402
from icon_style import INK, SHAPES, SVG, brighten, deepen  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/home-preview/logo-options"
PAPER = "#fffdfa"
INK_DEEP = "#1f352b"
BEAN = "#c2979a"        # 豆沙，爱心的颜色
SAMPLE = ["signtrace", "dictionary", "shouyu-shitingshuo", "skull", "perfectmenu", "flyinghands",
          "chuanqinghuiyi", "codenames", "jieguo", "shouyu-pass", "pinhaoke", "2026-year-end-summary"]
SEALS = {"黛绿": "#3e6b5d", "靛青": "#3f5c84", "赭石": "#ad5f3f", "藤黄": "#b98a32", "紫檀": "#835a72", "胭脂": "#b04f5b"}
SEAL_HUES = {"黛绿": 150, "靛青": 212, "赭石": 18, "藤黄": 42, "紫檀": 300, "胭脂": 352}


def hls(colour):
    red, green, blue = (int(colour[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return colorsys.rgb_to_hls(red, green, blue)


def mix(colour, other, amount):
    a = [int(colour[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(other[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * amount):02x}" for x, y in zip(a, b))


def is_hex(colour):
    return re.fullmatch(r"#[0-9a-f]{6}", colour or "") is not None


def is_pink(colour):
    hue, light, saturation = hls(colour)
    return saturation > .18 and light > .45 and (hue * 360 > 318 or hue * 360 < 12)


def source(project_id):
    text = build_home.icon_original(project_id).with_suffix(".svg").read_text(encoding="utf-8")
    recolour = icon_style.RECOLOUR.get(project_id, {})
    for old, new in recolour.items():
        text = text.replace(old, new)
    return text


def dominant(text):
    """The colour that covers the most of the drawing, ignoring the ink and near-neutral tints."""
    picture = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=text.encode(), output_width=96, output_height=96))).convert("RGBA")
    pixels = picture.get_flattened_data() if hasattr(picture, "get_flattened_data") else picture.getdata()
    counts = Counter("#%02x%02x%02x" % pixel[:3] for pixel in pixels if pixel[3] == 255)
    palette = set(re.findall(r'fill="(#[0-9a-fA-F]{6})"', text.lower()))
    ranked = [colour for colour, _ in counts.most_common() if colour in palette and colour != INK]
    lively = [colour for colour in ranked if hls(colour)[2] > .2 and hls(colour)[1] < .84]
    return (lively or ranked or ["#aec2b1"])[0]


def restyle(text, paint):
    """A copy of the drawing where `paint(fill, stroke, width)` returns the new (fill, stroke, width, extra attributes) of every shape."""
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


def wrap(body, defs="", view="0 0 256 256"):
    return f'<svg xmlns="{SVG}" viewBox="{view}" aria-hidden="true"><defs>{defs}</defs>{body}</svg>'


# 1 墨线 ----------------------------------------------------------------------------------------
def ink(text, uid):
    def paint(fill, stroke, width):
        line = INK_DEEP
        if is_hex(stroke) and stroke != INK and stroke != "none":
            line = BEAN if is_pink(stroke) else INK_DEEP
        if fill == INK:
            return INK_DEEP, "none", 0, {}
        if is_hex(fill):
            fill = mix(BEAN, PAPER, .38) if is_pink(fill) else PAPER
        return fill, line if stroke != "none" else "none", min(width, 13) * .46, {}
    return wrap(restyle(text, paint))


# 2 套印（已选定，正式画法在 icon_riso.py）-------------------------------------------------
from icon_riso import riso  # noqa: E402


# 3 印章 ----------------------------------------------------------------------------------------
def seal_colour(text):
    hue = hls(dominant(text))[0] * 360
    name = min(SEAL_HUES, key=lambda key: min(abs(SEAL_HUES[key] - hue), 360 - abs(SEAL_HUES[key] - hue)))
    return SEALS[name]


def seal(text, uid):
    ground = seal_colour(text)

    def paint(fill, stroke, width):
        if fill == INK:
            return PAPER, "none", 0, {}
        if is_hex(fill):
            fill = PAPER if is_pink(fill) else ground
        return fill, (PAPER if stroke != "none" else "none"), min(width, 13) * .62, {}
    rough = (f'<filter id="r{uid}" x="-5%" y="-5%" width="110%" height="110%">'
             '<feTurbulence type="fractalNoise" baseFrequency=".045" numOctaves="2" seed="3" result="w"/>'
             '<feDisplacementMap in="SourceGraphic" in2="w" scale="5" result="d"/>'
             '<feTurbulence type="fractalNoise" baseFrequency=".8" numOctaves="1" seed="9" result="s"/>'
             '<feColorMatrix in="s" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -24 17.4" result="k"/>'
             '<feComposite in="d" in2="k" operator="in"/></filter>')
    body = (f'<g filter="url(#r{uid})"><rect x="14" y="14" width="228" height="228" rx="40" fill="{ground}"/>'
            f'<g transform="translate(128 128) scale(.74) translate(-128 -128)">{restyle(text, paint)}</g></g>')
    return wrap(body, rough)


# 4 彩铅 ----------------------------------------------------------------------------------------
def pencil(text, uid):
    patterns, seen = [], {}

    def hatch(colour):
        if colour not in seen:
            key = f"h{uid}{len(seen)}"
            seen[colour] = key
            patterns.append(f'<pattern id="{key}" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(-38)">'
                            f'<rect width="7" height="7" fill="{mix(colour, PAPER, .5)}"/>'
                            f'<path d="M0 1.6H7M0 5.1H7" stroke="{deepen(colour, .08)}" stroke-width="2.1" stroke-opacity=".9"/></pattern>')
        return f"url(#{seen[colour]})"

    def paint(fill, stroke, width):
        if fill == INK:
            return deepen("#4b5d54", .25), "none", 0, {}
        base = brighten(fill) if is_hex(fill) else None
        line = deepen(base, .45) if base else (deepen(brighten(stroke), .1) if is_hex(stroke) and stroke != INK else "#33463c")
        return (hatch(base) if base else "none"), (line if stroke != "none" else "none"), min(width, 13) * .5, {}
    body = restyle(text, paint)
    wobble = (f'<filter id="w{uid}"><feTurbulence type="fractalNoise" baseFrequency=".06" numOctaves="2" seed="5" result="t"/>'
              '<feDisplacementMap in="SourceGraphic" in2="t" scale="3.2"/></filter>')
    return wrap(f'<g filter="url(#w{uid})">{body}</g>', wobble + "".join(patterns))


# 5 剪纸 ----------------------------------------------------------------------------------------
def paper(text, uid):
    last = ["#ece2cf"]

    def paint(fill, stroke, width):
        extra = {"filter": f"url(#p{uid})"}
        if fill == INK:
            return deepen(last[0], .5), "none", 0, extra
        if is_hex(fill):
            last[0] = brighten(fill)
            if hls(last[0])[1] > .9:  # a near-white palm would vanish on the page
                last[0] = mix(last[0], "#f3cdb6", .45)
            return last[0], "none", 0, extra
        if is_hex(stroke) and stroke != INK:
            return "none", brighten(stroke), width * 1.15, extra
        if stroke == INK:
            return "none", deepen(last[0], .3), width * .8, extra
        return fill, stroke, width, extra
    # 每张纸片向右下投一块实色阴影，再蒙一层很淡的纸纤维
    shadow = (f'<filter id="p{uid}" x="-10%" y="-10%" width="125%" height="125%">'
              '<feFlood flood-color="#1f352b" flood-opacity=".16"/><feComposite in2="SourceAlpha" operator="in"/>'
              '<feOffset dx="3.2" dy="4.2" result="s"/>'
              '<feTurbulence type="fractalNoise" baseFrequency=".75" numOctaves="2" seed="11" result="f"/>'
              '<feColorMatrix in="f" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .35 -.14" result="w"/>'
              '<feComposite in="w" in2="SourceAlpha" operator="in" result="fib"/>'
              '<feMerge><feMergeNode in="s"/><feMergeNode in="SourceGraphic"/><feMergeNode in="fib"/></feMerge></filter>')
    return wrap(restyle(text, paint), shadow)


SCHEMES = [
    ("墨线", "深墨绿细线勾勒，大片留白，只在爱心处点一笔豆沙色。像书籍里的插图小品，最安静、最克制。", ink),
    ("套印", "孔版印刷的味道：颜色和线条分两版印，彼此错开一点，色块里带油墨颗粒。有印刷品的质感，也最活泼。", riso),
    ("印章", "图案以留白反刻进一方深色印章，六种传统颜色，边缘带钤印的毛边。最有中文书卷气，也最端庄。", seal),
    ("彩铅", "浅色打底，同色彩铅斜向排线，轮廓线略带手抖。和首屏那只手是同一种画法，整页最统一。", pencil),
    ("剪纸", "不描边，每块颜色是一张纸片，叠在下面的纸片上投出一小块实色阴影，带淡淡的纸纤维。最有层次和手作感。", paper),
]


def main():
    content = build_home.shared_build()[0]()
    projects = {project["id"]: project for project in content["projects"]}
    sections = []
    for number, (name, note, draw) in enumerate(SCHEMES, 1):
        tiles = []
        for index, project_id in enumerate(SAMPLE):
            art = draw(source(project_id), f"{number}x{index}")
            project = projects[project_id]
            tiles.append(f'<li><span class="art">{art}</span><div><h3>{escape(project["title"])}</h3><p>{escape(project["description"])}</p></div></li>')
        large = "".join(f'<span class="big">{draw(source(pid), f"{number}b{i}")}</span>' for i, pid in enumerate(["signtrace", "flyinghands", "jieguo"]))
        sections.append(f'<section id="s{number}"><header><span class="no">{number}</span><h2>{name}</h2><p>{escape(note)}</p></header>'
                        f'<div class="bigs">{large}</div><ul>{"".join(tiles)}</ul></section>')
    nav = "".join(f'<a href="#s{n}">{n}　{name}</a>' for n, (name, _, _) in enumerate(SCHEMES, 1))
    page = f"""<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>作品图标五种方案</title>
<style>
:root {{ --ink:#1f352b; --ink2:#2f4439; --ink3:#4b5d54; --hair:rgba(31,53,43,.16); }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:{PAPER}; color:var(--ink); font:400 16px/1.8 "PingFang SC","Noto Sans SC",sans-serif; }}
h1,h2,h3 {{ margin:0; font-family:"Songti SC","Noto Serif SC",serif; font-weight:600; }}
main {{ width:min(1180px,100% - 44px); margin:0 auto; padding:56px 0 120px; }}
h1 {{ font-size:clamp(30px,4vw,46px); letter-spacing:.08em; }}
.lede {{ margin:14px 0 0; color:var(--ink2); }}
nav {{ position:sticky; top:0; z-index:3; display:flex; gap:28px; overflow-x:auto; margin-top:28px; padding:14px 0; border-block:1px solid var(--hair); background:rgba(255,253,250,.95); font-family:"Songti SC",serif; letter-spacing:.12em; white-space:nowrap; }}
nav a {{ color:var(--ink2); text-decoration:none; }}
section {{ padding:72px 0 24px; scroll-margin-top:60px; }}
header {{ display:grid; grid-template-columns:auto 1fr; gap:4px 18px; align-items:baseline; }}
.no {{ grid-row:span 2; font:italic 400 54px/1 Georgia,serif; color:{BEAN}; }}
h2 {{ font-size:32px; letter-spacing:.14em; }}
header p {{ margin:0; max-width:46em; color:var(--ink2); }}
.bigs {{ display:flex; gap:clamp(20px,5vw,72px); margin:40px 0 44px; }}
.big {{ width:clamp(96px,17vw,200px); }}
ul {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(250px,1fr)); gap:40px 44px; margin:0; padding:0; list-style:none; }}
li {{ display:grid; grid-template-columns:84px 1fr; gap:16px; align-items:start; }}
.art svg, .big svg {{ display:block; width:100%; height:auto; overflow:visible; }}
h3 {{ font-size:19px; line-height:1.45; letter-spacing:.04em; }}
li p {{ margin:6px 0 0; font-size:15px; line-height:1.75; color:var(--ink2); }}
@media (max-width:600px) {{ li {{ grid-template-columns:72px 1fr; }} }}
</style>
<main><h1>作品图标五种方案</h1>
<p class="lede">每种方案都由设计者的原稿自动重画，图案不变，只换画法。每组先放三枚大图看细节，下面是放在作品列表里的实际大小。奶家麻将、手小语、小爱、手语文化节四枚是图片，选定方案后再单独配套处理。</p>
<nav>{nav}</nav>{"".join(sections)}</main></html>
"""
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "index.html").write_text(page, encoding="utf-8")
    print(OUT / "index.html")


if __name__ == "__main__":
    main()
