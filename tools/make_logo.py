#!/usr/bin/env python3
"""Generate the DC Consulting logo lockups as SVG with text converted to outlines.

Needs: fonttools (dev only). Fonts: tools/fonts/SourceSerif4.ttf (SIL OFL).
Change NAME and re-run to rebuild every lockup if the company is renamed.
Writes to src/img/brand/.
"""
import os
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "src/img/brand")
NAME = "DC Consulting"
TRACK = 0.012  # letter-spacing in em

MARK_PATHS = (
    '<path d="M14 12H30C44 12 52 20.5 52 32C52 43.5 44 52 30 52H14V12Z" stroke="{m}" stroke-width="6" stroke-linejoin="round"/>'
    '<path d="M38 23C30 23 25 27 25 32C25 37 30 41 38 41" stroke="{m}" stroke-width="5.5" stroke-linecap="round"/>'
    '<rect x="11" y="28" width="6" height="8" rx="1" fill="{a}"/>'
)

_FONT = {}

def outline(text, size, wght=600, opsz=36):
    key = (wght, opsz)
    if key not in _FONT:
        f = TTFont(os.path.join(ROOT, "tools/fonts/SourceSerif4.ttf"))
        _FONT[key] = instancer.instantiateVariableFont(f, {"wght": wght, "opsz": opsz})
    f = _FONT[key]
    gs, cmap, upm = f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm
    s = size / upm
    x, parts = 0.0, []
    for ch in text:
        g = cmap[ord(ch)]
        pen = SVGPathPen(gs, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
        gs[g].draw(TransformPen(pen, (s, 0, 0, -s, x, 0)))
        d = pen.getCommands()
        if d:
            parts.append(d)
        x += gs[g].width * s + TRACK * size
    return " ".join(parts), x - TRACK * size

def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:g} {h:g}" fill="none">'
            f'<title>{title}</title>{body}</svg>\n')

def horizontal(m, a, t):
    mh = 40
    sc = mh / 64
    d, w = outline(NAME, 27)
    gap = 12
    body = (f'<g transform="scale({sc:g})">{MARK_PATHS.format(m=m, a=a)}</g>'
            f'<path transform="translate({mh + gap:g} 28.4)" fill="{t}" d="{d}"/>')
    return svg(round(mh + gap + w, 1), mh, body, NAME)

def stacked(m, a, t):
    mh = 56
    sc = mh / 64
    d, w = outline(NAME, 24)
    W = max(w, mh)
    body = (f'<g transform="translate({(W - mh) / 2:g} 0) scale({sc:g})">{MARK_PATHS.format(m=m, a=a)}</g>'
            f'<path transform="translate({(W - w) / 2:g} {mh + 28})" fill="{t}" d="{d}"/>')
    return svg(round(W, 1), mh + 36, body, NAME)

VARIANTS = {
    "": ("#1C3556", "#C1A066", "#17263D"),
    "-mono-navy": ("#1C3556", "#1C3556", "#1C3556"),
    "-mono-black": ("#000000", "#000000", "#000000"),
    "-reverse": ("#FFFFFF", "#C1A066", "#FFFFFF"),
}

def main():
    for suffix, (m, a, t) in VARIANTS.items():
        for kind, fn in (("horizontal", horizontal),):
            name = "logo-horizontal.svg" if not suffix else f"logo{suffix}.svg"
            open(os.path.join(OUT, name), "w").write(fn(m, a, t))
    open(os.path.join(OUT, "logo-stacked.svg"), "w").write(stacked(*VARIANTS[""]))
    print("logos written")

if __name__ == "__main__":
    main()
