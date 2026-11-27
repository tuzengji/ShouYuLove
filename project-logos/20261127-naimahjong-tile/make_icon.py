"""Print the 奶麻 character onto the mahjong tile and save the 奶家麻将 icon.

    python3 -B project-logos/20261127-naimahjong-tile/make_icon.py <character image>

The tile (tile.svg) is drawn in the site's style: brightened colours, each shape outlined in a
deeper tone of its own colour. The character picture may have a transparent or a plain white
background; white is cut away from the edges inwards. Writes naimahjong.png (1024px, transparent)
next to this script; build_home.py picks it up through ICON_SETS.
"""
import io
import sys
from collections import deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "scripts"))
import legacy_pages  # noqa: E402,F401  (sets up cairosvg on macOS)
import cairosvg  # noqa: E402
import icon_style  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

SIZE = 1024
FACE = (60, 36, 118, 168)  # the printable face inside the tile, in the 256 grid
FACE_RADIUS = 18


def cut_out(picture):
    """Make a white background transparent, starting from the border so white inside the figure stays."""
    picture = picture.convert("RGBA")
    if picture.getchannel("A").getextrema()[0] < 250:
        return picture
    width, height = picture.size
    pixels = picture.load()
    near_white = lambda x, y: min(pixels[x, y][:3]) > 236
    seen, queue = set(), deque()
    for x in range(width):
        queue.extend([(x, 0), (x, height - 1)])
    for y in range(height):
        queue.extend([(0, y), (width - 1, y)])
    while queue:
        x, y = queue.popleft()
        if (x, y) in seen or not (0 <= x < width and 0 <= y < height) or not near_white(x, y):
            continue
        seen.add((x, y))
        queue.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])
    mask = Image.new("L", picture.size, 255)
    for point in seen:
        mask.putpixel(point, 0)
    picture.putalpha(mask.filter(ImageFilter.GaussianBlur(1.2)))
    return picture


def main(source):
    tile = icon_style.tonal((HERE / "tile.svg").read_text(encoding="utf-8"))
    icon = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=tile.encode(), output_width=SIZE, output_height=SIZE))).convert("RGBA")
    figure = cut_out(Image.open(source))
    figure = figure.crop(figure.getchannel("A").point(lambda value: 255 if value >= 128 else 0).getbbox())
    scale = SIZE / 256
    left, top, width, height = (value * scale for value in FACE)
    # The character stands on the bottom of the printed face, filling its width; whatever the
    # picture cuts off at the bottom disappears into the face's rounded frame.
    fit = min(width / figure.width, (height - 14 * scale) / figure.height)
    figure = figure.resize((round(figure.width * fit), round(figure.height * fit)), Image.Resampling.LANCZOS)
    face = Image.new("RGBA", (round(width), round(height)), (0, 0, 0, 0))
    face.alpha_composite(figure, (round((width - figure.width) / 2), round(height - figure.height)))
    frame = Image.new("L", (round(width) * 4, round(height) * 4), 0)
    ImageDraw.Draw(frame).rounded_rectangle((0, 0, round(width) * 4 - 1, round(height) * 4 - 1), radius=FACE_RADIUS * scale * 4, fill=255)
    frame = frame.resize(face.size, Image.Resampling.LANCZOS)
    face.putalpha(Image.composite(face.getchannel("A"), Image.new("L", face.size, 0), frame))
    icon.alpha_composite(face, (round(left), round(top)))
    icon.save(HERE / "naimahjong.png", optimize=True)
    print("wrote", HERE / "naimahjong.png")


if __name__ == "__main__":
    main(sys.argv[1])
