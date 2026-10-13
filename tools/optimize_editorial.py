#!/usr/bin/env python3
"""Process and optimize editorial photographic assets.
Generates responsive AVIF, WebP, and JPEG files and outputs sizes.json.
"""
import os, json
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "tools/originals/editorial")
OUT = os.path.join(ROOT, "src/img/editorial")
os.makedirs(OUT, exist_ok=True)

WIDTHS = [480, 800, 1200]

def main():
    sizes = {}
    files = sorted([f for f in os.listdir(SRC) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    
    for fname in files:
        base_name, _ = os.path.splitext(fname)
        src_path = os.path.join(SRC, fname)
        im = Image.open(src_path).convert("RGB")
        
        orig_w, orig_h = im.size
        aspect = round(orig_h / orig_w, 4)
        
        asset_info = {
            "aspect_ratio": aspect,
            "original_size": [orig_w, orig_h],
            "variants": {}
        }
        
        target_widths = [w for w in WIDTHS if w <= orig_w]
        if orig_w not in target_widths and orig_w > 1200:
            target_widths.append(min(orig_w, 1400))
            
        for w in target_widths:
            h = round(orig_h * w / orig_w)
            resized = im.resize((w, h), Image.LANCZOS)
            
            variant_files = {}
            # AVIF
            avif_name = f"{base_name}-{w}w.avif"
            avif_path = os.path.join(OUT, avif_name)
            resized.save(avif_path, "AVIF", quality=55)
            variant_files["avif"] = {"file": avif_name, "bytes": os.path.getsize(avif_path)}
            
            # WebP
            webp_name = f"{base_name}-{w}w.webp"
            webp_path = os.path.join(OUT, webp_name)
            resized.save(webp_path, "WEBP", quality=80, method=6)
            variant_files["webp"] = {"file": webp_name, "bytes": os.path.getsize(webp_path)}
            
            # JPEG
            jpg_name = f"{base_name}-{w}w.jpg"
            jpg_path = os.path.join(OUT, jpg_name)
            resized.save(jpg_path, "JPEG", quality=82, optimize=True, progressive=True)
            variant_files["jpeg"] = {"file": jpg_name, "bytes": os.path.getsize(jpg_path)}
            
            asset_info["variants"][str(w)] = {
                "width": w,
                "height": h,
                "files": variant_files
            }
            
        sizes[base_name] = asset_info
        largest_w = str(target_widths[-1])
        webp_sz = asset_info["variants"][largest_w]["files"]["webp"]["bytes"] // 1024
        print(f"Processed {base_name}: {orig_w}x{orig_h} -> max {largest_w}w ({webp_sz} KB WebP)")
        
    sizes_path = os.path.join(OUT, "sizes.json")
    with open(sizes_path, "w", encoding="utf-8") as f:
        json.dump(sizes, f, indent=2)
    print(f"\nWrote metadata for {len(sizes)} editorial assets to {sizes_path}")

if __name__ == "__main__":
    main()
