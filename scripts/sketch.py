"""Redraw the brand mark the way a hand would: a brush line that wavers and swells,
coloured-pencil hatching that stays roughly inside it, and a few frames that differ
slightly so the drawing can 'boil' like hand-made animation.

Everything is generated from the approved mark's own outlines with fixed seeds,
so the drawings are reproducible and need no extra artwork.
"""

import math
import random
import re

INK = "#3d4f46"
SHIFT = (2.0, -11.0)  # the mark's own group transform
FRAMES = 3
POP = (9.0, 8.5)  # where the hover heart sits in the icon overlay's 100-unit box; styles/next.css turns around the same point


def flatten(d, steps=12):
    """Absolute M, L, H, V, C and Z are all the mark uses."""
    tokens = re.findall(r"[MLHVCZ]|-?\d*\.?\d+", d)
    points, i, x, y, command = [], 0, 0.0, 0.0, ""
    while i < len(tokens):
        if tokens[i].isalpha():
            command = tokens[i]
            i += 1
            if command == "Z":
                continue
        take = lambda count: [float(value) for value in tokens[i:i + count]]
        if command in "ML":
            x, y = take(2); i += 2
            points.append((x, y))
        elif command == "H":
            x, = take(1); i += 1
            points.append((x, y))
        elif command == "V":
            y, = take(1); i += 1
            points.append((x, y))
        elif command == "C":
            x1, y1, x2, y2, x3, y3 = take(6); i += 6
            for step in range(1, steps + 1):
                t = step / steps; u = 1 - t
                points.append((u ** 3 * x + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t ** 3 * x3,
                               u ** 3 * y + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t ** 3 * y3))
            x, y = x3, y3
    return [(px + SHIFT[0], py + SHIFT[1]) for px, py in points]


def resample(points, spacing, closed=False):
    """Evenly spaced points along a polyline; a closed result does not repeat its first point."""
    path = points + [points[0]] if closed else points
    spans = [math.dist(a, b) for a, b in zip(path, path[1:])]
    total = sum(spans)
    count = max(2, round(total / spacing))
    out, index, walked = [], 0, 0.0
    for step in range(count if closed else count + 1):
        target = total * step / count
        while index < len(spans) - 1 and walked + spans[index] < target:
            walked += spans[index]; index += 1
        t = (target - walked) / spans[index] if spans[index] else 0
        a, b = path[index], path[index + 1]
        out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


def number(value):
    text = f"{value:.1f}"
    return text[:-2] if text.endswith(".0") else text


def smooth(points, closed=True):
    """Quadratic curves through the midpoints, so resampled outlines read as one stroke."""
    mid = lambda a, b: ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    pair = lambda p: number(p[0]) + " " + number(p[1])
    if closed:
        ring = points + points[:2]
        return "M" + pair(mid(ring[0], ring[1])) + "".join(
            "Q" + pair(ring[i]) + " " + pair(mid(ring[i], ring[i + 1])) for i in range(1, len(points) + 1)) + "Z"
    return "M" + pair(points[0]) + "".join(
        "Q" + pair(points[i]) + " " + pair(mid(points[i], points[i + 1]) if i < len(points) - 2 else points[i + 1])
        for i in range(1, len(points) - 1))


def brush(points, rng, half=3.0, wobble=1.0, closed=False, lap=10.0, taper=12.0, spacing=3.0, blunt_start=False):
    """A stroke as a filled shape: it drifts off the true outline, swells and thins, and tapers at its ends.

    A closed outline starts somewhere unremarkable and runs a little past its start, as a pen would.
    """
    line = resample(points, spacing, closed)
    if closed:
        start = rng.randrange(len(line))
        line = line[start:] + line[:start]
        line = line + line[:max(2, int(lap / spacing))]
    total = (len(line) - 1) * spacing
    phase = [rng.uniform(0, math.tau) for _ in range(4)]
    left, right = [], []
    for i, point in enumerate(line):
        a, b = line[max(0, i - 2)], line[min(len(line) - 1, i + 2)]
        length = math.dist(a, b) or 1
        normal = (-(b[1] - a[1]) / length, (b[0] - a[0]) / length)
        along = i * spacing
        drift = wobble * (.7 * math.sin(along / 23 + phase[0]) + .4 * math.sin(along / 9.5 + phase[1]))
        swell = 1 + .2 * math.sin(along / 17 + phase[2]) + .1 * math.sin(along / 6 + phase[3])
        end = total - along if blunt_start else min(along, total - along)
        width = half * swell * min(1, .22 + .78 * end / taper)
        centre = (point[0] + normal[0] * drift, point[1] + normal[1] * drift)
        left.append((centre[0] + normal[0] * width, centre[1] + normal[1] * width))
        right.append((centre[0] - normal[0] * width, centre[1] - normal[1] * width))
    return smooth(left + right[::-1])


def inward(points, amount):
    """Move a closed outline toward its inside (negative amounts grow it)."""
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(points, points[1:] + points[:1]))
    sign = 1 if area > 0 else -1
    out = []
    for i, point in enumerate(points):
        a, b = points[i - 1], points[(i + 1) % len(points)]
        length = math.dist(a, b) or 1
        out.append((point[0] - sign * (b[1] - a[1]) / length * amount, point[1] + sign * (b[0] - a[0]) / length * amount))
    return out


def wash(shape, rng, inset=1.5, wobble=1.3, slip=(1.6, 2.0)):
    """The flat colour under the pencil: a little short of the line, and printed slightly out of register."""
    ring = inward(resample(shape, 5, closed=True), inset)
    phase = [rng.uniform(0, math.tau) for _ in range(2)]
    ring = [(x + slip[0] + wobble * math.sin(i / 3.1 + phase[0]), y + slip[1] + wobble * math.sin(i / 2.3 + phase[1]))
            for i, (x, y) in enumerate(ring)]
    return smooth(ring)


def hatch(shape, rng, angle=-38.0, gap=5.2, inset=3.0):
    """Pencil strokes across a shape, each stopping a little short of the outline."""
    ring = inward(resample(shape, 3, closed=True), inset)
    cos, sin = math.cos(math.radians(-angle)), math.sin(math.radians(-angle))
    turned = [(x * cos - y * sin, x * sin + y * cos) for x, y in ring]
    back = lambda x, y: (x * cos + y * sin, -x * sin + y * cos)
    low, high = min(y for _, y in turned), max(y for _, y in turned)
    strokes, y = [], low + gap * .6
    while y < high:
        crossings = sorted(a[0] + (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1])
                           for a, b in zip(turned, turned[1:] + turned[:1]) if (a[1] > y) != (b[1] > y))
        for start, stop in zip(crossings[::2], crossings[1::2]):
            start += rng.uniform(.3, 3.2); stop -= rng.uniform(.3, 3.2)
            if stop - start < 4:
                continue
            a, b = back(start, y + rng.uniform(-.7, .7)), back(stop, y + rng.uniform(-.7, .7))
            middle = back((start + stop) / 2, y + rng.uniform(-1.4, 1.4))
            strokes.append("M" + number(a[0]) + " " + number(a[1]) + "Q" + number(middle[0]) + " " + number(middle[1])
                           + " " + number(b[0]) + " " + number(b[1]))
        y += gap * rng.uniform(.82, 1.2)
    return "".join(strokes)


def circle(cx, cy, radius, count=48):
    return [(cx + radius * math.cos(math.tau * i / count), cy + radius * math.sin(math.tau * i / count)) for i in range(count)]


def star(cx, cy, outer, inner):
    return [(cx + (outer if i % 2 == 0 else inner) * math.cos(math.tau * i / 8 - math.pi / 2),
             cy + (outer if i % 2 == 0 else inner) * math.sin(math.tau * i / 8 - math.pi / 2)) for i in range(8)]


def scribble(rng, width=200.0):
    """A quick underline: one stroke that sags a little and thins toward its end."""
    phase = rng.uniform(0, math.tau)
    line = [(x, 6 + 1.6 * math.sin(x / width * math.pi + phase) + rng.uniform(-.25, .25)) for x in range(2, int(width) - 1, 6)]
    return brush(line, rng, half=2.2, wobble=.5, taper=26, spacing=6)


def loop(rng):
    """One turn of crayon around an icon, the way you circle something you like; it runs past its own start."""
    turns, count = 1.13, 46
    start = rng.uniform(2.2, 2.6)  # the pen comes down at the lower left
    phase = [rng.uniform(0, math.tau) for _ in range(2)]
    points = []
    for i in range(count + 1):
        t = i / count
        angle = start + math.tau * turns * t
        radius = 43 + 3.2 * t + .9 * math.sin(angle * 3 + phase[0]) + .5 * math.sin(angle * 5 + phase[1])
        cos, sin = math.cos(angle), math.sin(angle)
        # Rounder than a circle would be flat: the loop follows the paper scrap, a touch squarer.
        reach = radius * (abs(cos) ** 2.3 + abs(sin) ** 2.3) ** (-1 / 2.3)
        points.append((50 + reach * cos, 50 + reach * sin))
    return smooth(points, closed=False)


def drawings(paths):
    """SVG definitions shared by both pages: static pencil fills plus FRAMES line variants of each drawing."""
    heart, hand, cuff, thumb = (flatten(paths[name]) for name in ("heart", "hand", "cuff", "thumb"))
    sleeve = [(-70.0, 142.0), (34.0, 142.0), (34.0, 204.0), (-70.0, 204.0)]
    rng = random.Random(20261127)
    pencil = lambda d, colour, width, opacity: (f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{width}" '
                                                 f'stroke-linecap="round" opacity="{opacity}"/>')
    ink = lambda d: f'<path d="{d}"/>'
    ribs = "".join(ink(brush([(x + rng.uniform(-.6, .6), 147.0), (x + rng.uniform(-.8, .8), 175.0), (x + rng.uniform(-.6, .6), 199.0)],
                             rng, half=1.0, wobble=.5, taper=8)) for x in (38.5, 44.0, 49.5, 55.0))
    parts = [
        # A cut-paper disc behind the heart gives the drawing its warmth without any gradient.
        f'<path id="sk-halo" d="{smooth(inward(circle(136, 104, 96), 0))}" fill="var(--halo, #f6e4d6)"/>',
        '<g id="sk-heart-fill">'
        f'<path d="{wash(heart, rng)}" fill="#dcb9bb"/>{pencil(hatch(heart, rng, -38, 5.0), "#b98489", 3.0, .62)}</g>',
        '<g id="sk-hand-fill">'
        f'<path d="{wash(sleeve, rng, 0, .8, (0, 1.5))}" fill="var(--sleeve-soft)"/>{pencil(hatch(sleeve, rng, -8, 8.5, 2), "var(--sleeve)", 2.6, .6)}'
        f'<path d="{wash(hand, rng)}" fill="#f4dfcf"/>{pencil(hatch(hand, rng, -24, 6.4), "#e3bfa8", 2.8, .6)}'
        f'<path d="{wash(cuff, rng, 1, .7, (1, 1.2))}" fill="var(--sleeve)"/><g fill="var(--sleeve-rib)" opacity=".8">{ribs}</g></g>',
    ]
    # Ink lines: each frame is the same drawing made again, never quite the same way twice.
    rays = [[(136 + r * math.cos(math.radians(a)), 75 + r * math.sin(math.radians(a))) for r in (60, 67, 75)] for a in (-64, -40, -16)]
    for frame in range(1, FRAMES + 1):
        parts.append(f'<g id="sk-heart-{frame}" fill="{INK}">{ink(brush(heart, rng, 3.1, 1.0, closed=True))}</g>')
        parts.append(
            f'<g id="sk-hand-{frame}" fill="{INK}">'
            + ink(brush(sleeve[:2], rng, 2.8, .9, blunt_start=True)) + ink(brush(sleeve[:1:-1], rng, 2.8, .9, blunt_start=True))
            + ink(brush(hand, rng, 3.1, 1.0, closed=True)) + ink(brush(thumb, rng, 2.9, .8))
            + ink(brush(cuff, rng, 2.9, .7, closed=True)) + '</g>')
        # What a pen adds around something precious: a few rays and two small stars.
        parts.append(
            f'<g id="sk-rays-{frame}" fill="{INK}">' + "".join(ink(brush(ray, rng, 1.9, .5, taper=7)) for ray in rays)
            + f'<path d="{smooth(star(84 + rng.uniform(-.6, .6), 34 + rng.uniform(-.6, .6), 10, 3.4))}" fill="#dcc88f"/>'
            + f'<path d="{smooth(star(196 + rng.uniform(-.5, .5), 100 + rng.uniform(-.5, .5), 6.5, 2.2))}" fill="#dcc88f"/></g>')
    for index in range(1, 5):
        parts.append(f'<path id="sk-line-{index}" d="{scribble(rng)}"/>')
    # What hovering adds to a work's icon, in a 100-unit box that reaches a little past the icon.
    for frame in range(1, FRAMES + 1):
        parts.append(f'<path id="sk-loop-{frame}" pathLength="1" d="{loop(rng)}"/>')
    # A small heart sits just off the icon's top left corner, with three rays on its far side.
    cx, cy = POP
    ray = lambda degrees: [(cx + r * math.cos(math.radians(degrees)), cy + r * math.sin(math.radians(degrees))) for r in (12.5, 15.5, 18.5)]
    parts.append(f'<g id="sk-pop-rays" fill="{INK}">' + "".join(ink(brush(ray(a), rng, .9, .2, taper=3, spacing=1)) for a in (-166, -131, -96)) + '</g>')
    tiny = [((x - 134) * .16 + cx, (y - 75) * .16 + cy) for x, y in heart]
    parts.append(f'<g id="sk-pop-heart"><path d="{smooth(resample(tiny, 1.2, closed=True))}" fill="#dcb9bb"/>'
                 f'<path d="{brush(tiny, rng, .95, .15, closed=True, lap=2.5, taper=3, spacing=1.1)}" fill="{INK}"/></g>')
    return ('<svg width="0" height="0" aria-hidden="true" focusable="false" style="position:absolute"><defs>'
            + "".join(parts) + '</defs></svg>')


def boil(name):
    """The frames of one drawing; CSS shows them in turn."""
    return '<g class="boil">' + "".join(f'<use href="#sk-{name}-{frame}"/>' for frame in range(1, FRAMES + 1)) + '</g>'


def heart_svg(rays=False, extra=""):
    return (f'<svg viewBox="82 30 104 90" aria-hidden="true"{extra}><use href="#sk-heart-fill"/>{boil("heart")}'
            + (f'<g class="rays">{boil("rays")}</g>' if rays else "") + '</svg>')


def hand_svg(rest_heart=True):
    heart = f'<g class="rest-heart"><use href="#sk-heart-fill"/>{boil("heart")}</g>' if rest_heart else ""
    return (f'<svg class="hand-svg" viewBox="0 20 240 210" aria-hidden="true"><use href="#sk-halo"/>'
            f'<use href="#sk-hand-fill"/>{boil("hand")}{heart}</svg>')


def pen_svg():
    """Laid over an icon and drawn in on hover: the crayon loop, then a small heart and two rays at the corner."""
    return (f'<svg class="tile-pen" viewBox="0 0 100 100" aria-hidden="true"><g class="loop">{boil("loop")}</g>'
            '<use class="pop-rays" href="#sk-pop-rays"/><g class="pop-heart"><use href="#sk-pop-heart"/></g></svg>')


def underline(index):
    return (f'<svg class="scribble" viewBox="0 0 200 12" preserveAspectRatio="none" aria-hidden="true">'
            f'<use href="#sk-line-{index % 4 + 1}"/></svg>')
