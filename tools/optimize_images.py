#!/usr/bin/env python3
"""Rebuild src/img/illustrations from tools/originals (deterministic, safe to re-run).

Per asset: optional crop, background flattening to exactly #FBFAF7 (removes glow/vignette),
then AVIF/WebP/JPEG at several widths (never upscaled) and sizes.json for width/height attrs.
"""
import json, os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "tools/originals")
OUT = os.path.join(ROOT, "src/img/illustrations")
BG = (251, 250, 247)
FLATTEN_TOL = 9

# crop = (left, top, right, bottom) in original pixels
ASSETS = {
    "hero-supply-route": {"crop": (40, 130, 1340, 690), "widths": [480, 800, 1200, 1300]},
    "commodity-rare-earths": {"widths": [480, 800, 1200]},
    "commodity-crude-oil": {"widths": [480, 800, 1200]},
    "commodity-gems": {"widths": [480, 800, 1200]},
}
BUDGET = {"hero-supply-route": 120_000}  # bytes at largest WebP
CARD_BUDGET = 60_000

def flatten(im):
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            p = px[x, y]
            if max(abs(p[0] - BG[0]), abs(p[1] - BG[1]), abs(p[2] - BG[2])) <= FLATTEN_TOL:
                px[x, y] = BG
    return im

def main():
    sizes = {}
    for name, cfg in ASSETS.items():
        im = Image.open(os.path.join(SRC, name + ".jpg")).convert("RGB")
        if "crop" in cfg:
            im = im.crop(cfg["crop"])
        im = flatten(im)
        sizes[name] = {"aspect_ratio": round(im.height / im.width, 4), "original_size": [im.width, im.height], "variants": {}}
        for w in cfg["widths"]:
            w = min(w, im.width)
            h = round(im.height * w / im.width)
            r = im.resize((w, h), Image.LANCZOS)
            files = {}
            for fmt, ext, kw in (("avif", "avif", {"quality": 55}), ("webp", "webp", {"quality": 80, "method": 6}),
                                 ("jpeg", "jpg", {"quality": 82, "optimize": True, "progressive": True})):
                fn = f"{name}-{w}w.{ext}"
                path = os.path.join(OUT, fn)
                r.save(path, fmt.upper(), **kw)
                files[fmt] = {"file": fn, "bytes": os.path.getsize(path)}
            sizes[name]["variants"][str(w)] = {"width": w, "height": h, "files": files}
        top = sizes[name]["variants"][str(min(cfg["widths"][-1], im.width))]["files"]["webp"]["bytes"]
        limit = BUDGET.get(name, CARD_BUDGET)
        print(f"{name}: {im.size} largest webp {top/1000:.0f} KB (budget {limit/1000:.0f} KB) {'OK' if top <= limit else 'OVER'}")
    # drop stale files from previous runs
    keep = {f["file"] for a in sizes.values() for v in a["variants"].values() for f in v["files"].values()}
    for f in os.listdir(OUT):
        if f.endswith((".avif", ".webp", ".jpg")) and f not in keep and any(f.startswith(n + "-") for n in ASSETS):
            os.remove(os.path.join(OUT, f))
    with open(os.path.join(OUT, "sizes.json"), "w") as f:
        json.dump(sizes, f, indent=2)

def hero_background():
    """content/assets/hero_background.png -> src/img/backgrounds/hero-slate-*.webp/jpg.
    Crops the bevelled slab edge and the corner watermark so only clean texture remains."""
    src = os.path.join(ROOT, "tools/originals/hero-background.png")
    if not os.path.exists(src):
        return
    out = os.path.join(ROOT, "src/img/backgrounds")
    os.makedirs(out, exist_ok=True)
    im = Image.open(src).convert("RGB").crop((60, 60, 1300, 680))
    for w in (800, 1240):
        r = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        r.save(os.path.join(out, f"hero-slate-{w}.webp"), "WEBP", quality=72, method=6)
        r.save(os.path.join(out, f"hero-slate-{w}.jpg"), "JPEG", quality=72, optimize=True, progressive=True)
    print("hero background:", {f: os.path.getsize(os.path.join(out, f)) // 1000 for f in sorted(os.listdir(out))})

if __name__ == "__main__":
    main()
    hero_background()
