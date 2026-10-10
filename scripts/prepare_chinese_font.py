#!/usr/bin/env python3
"""Generate vector MSDF Chinese glyphs while retaining the browser font and Latin glyphs."""

import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from fontTools.ttLib import TTFont
from fontTools import subset
from PIL import Image, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "output/deployment/shouyulove-jieguo-20261009/font-source"
FONT = DIRECTORY / "SweiSpringSugarCJKsc-Regular.ttf"
MSDFGEN = ROOT / "output/tools/msdfgen-v1.13/build/msdfgen"
LABELS = "点击了解 向下探索 作品集 作品导航 首页 返回 心创组 开启声音 关闭 静音 设计者"


def main():
    text = (ROOT / "content-source.md").read_text() + LABELS
    characters = sorted(c for c in set(text) if ord(c) > 127)
    native = TTFont(FONT)
    cmap = native.getBestCmap()
    assert all(ord(c) in cmap for c in characters), "Missing Chinese font glyph"
    browser_path = DIRECTORY / "swei-spring-serif.woff2"
    browser_unchanged = browser_path.exists() and set(TTFont(browser_path).getBestCmap()) == {ord(c) for c in characters}
    if not browser_unchanged:
        browser_font = TTFont(FONT)
        options = subset.Options()
        options.flavor = "woff2"
        sub = subset.Subsetter(options=options)
        sub.populate(unicodes={ord(c) for c in characters})
        sub.subset(browser_font)
        # Name the modified Chinese-only subset separately; the original English faces stay unchanged.
        preview_names={1:"ShouYu Swei Spring Chinese",2:"Regular",3:"ShouYuSweiSpringChinese-1",4:"ShouYu Swei Spring Chinese Regular",6:"ShouYuSweiSpringChinese-Regular",16:"ShouYu Swei Spring Chinese",17:"Regular",18:"ShouYu Swei Spring Chinese Regular",21:"ShouYu Swei Spring Chinese",22:"Regular"}
        for record in browser_font["name"].names:
            if record.nameID in preview_names:record.string=preview_names[record.nameID].encode(record.getEncoding())
        if "CFF " in browser_font:
            cff=browser_font["CFF "].cff
            cff.fontNames=[preview_names[6]]
            cff.topDictIndex[0].FamilyName=preview_names[1]
            cff.topDictIndex[0].FullName=preview_names[4]
        browser_font.flavor = "woff2"
        browser_font.save(browser_path)
    assert MSDFGEN.exists(), "Build the pinned msdfgen v1.13 tool; see README.md"
    small = ImageFont.truetype(str(FONT), 42)
    atlas = Image.new("RGB", (1024, 2048))
    chars = []
    glyph_directory = DIRECTORY / "glyphs"
    glyph_directory.mkdir(exist_ok=True)
    def render_glyph(item):
        char, width, height, left, top = item
        output = glyph_directory / f"{ord(char):04x}.png"
        subprocess.run([str(MSDFGEN), "msdf", "-font", str(FONT), hex(ord(char)), "-emnormalize",
                        "-dimensions", str(width), str(height), "-scale", "42",
                        "-translate", str((2-left)/42), str((height-2+top)/42),
                        "-pxrange", "4", "-o", str(output)], check=True, capture_output=True)
        return output
    jobs = []
    for index, char in enumerate(characters):
        left, top, right, bottom = small.getbbox(char, anchor="ls")
        width, height = right-left+4, bottom-top+4
        assert width <= 64 and height <= 64
        x, y = (index % 16)*64, (index // 16)*64
        if bottom > top and not char.isspace():
            jobs.append((char, width, height, left, top))
        else:
            width = height = 0
        chars.append(dict(id=ord(char),index=native.getGlyphID(cmap[ord(char)]),char=char,width=width,height=height,
                          xoffset=left-2,yoffset=37+top-2,xadvance=small.getlength(char),chnl=15,x=x,y=y,page=0))
    by_character = {item["char"]:item for item in chars}
    with ThreadPoolExecutor(max_workers=6) as executor:
        for job, output in zip(jobs, executor.map(render_glyph, jobs)):
            item = by_character[job[0]]
            image = Image.open(output).convert("RGB")
            pixels = np.asarray(image)
            assert np.any(pixels[:, :, 0] != pixels[:, :, 1]), "Not a multi-channel distance field: " + job[0]
            atlas.paste(image, (item["x"], item["y"]))
    result = dict(pages=["chinese-atlas-0.png"],chars=chars,info=dict(size=42),
                  common=dict(lineHeight=42,base=37,scaleW=1024,scaleH=2048,pages=1),
                  distanceField=dict(fieldType="msdf",distanceRange=4),kernings=[])
    atlas.save(DIRECTORY/"chinese-atlas-0.png",optimize=True)
    (DIRECTORY/"chinese-font.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    assert all(c["index"]>0 for c in chars), "Fallback glyph in atlas"
    print(f"Verified {len(chars)} Chinese glyphs; original Latin atlas retained separately.")


if __name__ == "__main__":
    main()
