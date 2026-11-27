"""Redraw the soft-colour icons brighter and without their heavy dark outline.

The drawings stay exactly as their designers made them. Two things change: the dusty colours are
lifted to clearer, livelier ones (`brighten`), and every shape is outlined in a deeper tone of its
own colour, with loose detail lines taking the tone of the shape drawn just before them, so no
icon carries the near-black ink any more.

Run after adding or changing an icon's SVG (needs cairosvg, with Homebrew's cairo on macOS):

    python3 -B scripts/icon_style.py

It writes the restyled SVG and a 1024px transparent PNG for every work whose icon has a vector
original into project-logos/<SET>/. build_home.py uses those, and falls back to the original PNG
for the icons that only exist as pictures.
"""

import colorsys
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SET = "20261127-同色描边"
SVG = "http://www.w3.org/2000/svg"
INK = "#4b5d54"  # the outline every icon in the set was drawn with
SHAPES = {"path", "rect", "circle", "ellipse", "line", "polyline", "polygon"}
THINNER = .62    # the tonal line is also lighter in weight
BRIGHT = 1.3     # how far the dusty colours are lifted: 0 keeps them, about 2 turns them candy-like
ET.register_namespace("", SVG)


def deepen(colour, amount, saturate=.07):
    """The same hue, darker and a little richer, as a pencil pressed harder."""
    red, green, blue = (int(colour[i:i + 2], 16) / 255 for i in (1, 3, 5))
    hue, light, saturation = colorsys.rgb_to_hls(red, green, blue)
    red, green, blue = colorsys.hls_to_rgb(hue, light * (1 - amount), min(1, saturation + saturate))
    return "#" + "".join(f"{round(value * 255):02x}" for value in (red, green, blue))


def brighten(colour, level=BRIGHT):
    """A clearer, livelier version of a dusty colour: more saturated, and pale tints a touch lighter."""
    red, green, blue = (int(colour[i:i + 2], 16) / 255 for i in (1, 3, 5))
    hue, light, saturation = colorsys.rgb_to_hls(red, green, blue)
    if saturation < .04:
        return colour
    if light > .84:
        light, saturation = min(.95, light + .03 * level), min(.9, saturation + .18 * level)
    else:
        light, saturation = light + (.7 - light) * .25 * level, min(.92, saturation * (1 + .55 * level) + .12 * level)
    red, green, blue = colorsys.hls_to_rgb(hue, light, saturation)
    return "#" + "".join(f"{round(value * 255):02x}" for value in (red, green, blue))


def tonal(text):
    """Return the icon's SVG brightened, with every dark outline replaced by a deeper tone of the colour it surrounds."""
    root = ET.fromstring(text)
    last = ["#ece2cf"]

    def walk(node, inherited):
        own = dict(inherited)
        for key in ("fill", "stroke", "stroke-width"):
            if node.get(key) is not None:
                own[key] = node.get(key)
        if node.tag.split("}")[-1] in SHAPES:
            fill = own.get("fill", "#000000").lower()
            stroke = own.get("stroke", "none").lower()
            width = float(own.get("stroke-width", "1") or 1)
            coloured = re.fullmatch(r"#[0-9a-f]{6}", fill) is not None and fill != INK
            if coloured:
                fill = brighten(fill)
            if re.fullmatch(r"#[0-9a-f]{6}", stroke) and stroke != INK:
                stroke = brighten(stroke)
            if stroke == INK and width > 0:
                stroke = deepen(fill if coloured else last[0], .36)
                width *= THINNER
            if fill == INK:
                fill = deepen(last[0], .4)
            if coloured:
                last[0] = fill
            node.set("fill", fill)
            node.set("stroke", stroke)
            node.set("stroke-width", f"{width:.1f}")
        else:  # every shape now states its own colours, so a group no longer needs to pass the ink down
            for key in ("fill", "stroke"):
                if (node.get(key) or "").lower() == INK:
                    del node.attrib[key]
        for child in node:
            walk(child, own)

    walk(root, {})
    return ET.tostring(root, encoding="unicode")


def main():
    import legacy_pages  # noqa: F401  (sets up cairosvg on macOS)
    import cairosvg
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import build_home
    parse_content, _ = build_home.shared_build()
    folder = ROOT / "project-logos" / SET
    folder.mkdir(exist_ok=True)
    for project in parse_content()["projects"]:
        source = build_home.icon_original(project["id"]).with_suffix(".svg")
        if not source.is_file():
            print("kept as a picture:", project["id"])
            continue
        drawing = tonal(source.read_text(encoding="utf-8"))
        (folder / source.name).write_text(drawing + "\n", encoding="utf-8")
        cairosvg.svg2png(bytestring=drawing.encode(), write_to=str(folder / (project["id"] + ".png")), output_width=1024, output_height=1024)
        print("redrawn:", project["id"])


if __name__ == "__main__":
    main()
