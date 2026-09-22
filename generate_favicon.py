#!/usr/bin/env python3
"""
Spaghetti Western Discovery — Favicon Generator
Creates favicon.ico, favicon-16x16.png, favicon-32x32.png, and apple-touch-icon.png
from a programmatically drawn western star/badge design.
"""

import struct
import zlib
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Pillow not available, using manual PNG generation")

OUTPUT_DIR = Path(__file__).parent

# ─── Colour Palette ──────────────────────────────────────────────────────────
BG_DARK    = (26, 20, 18, 255)      # #1a1412 — dark wood background
GOLD       = (197, 160, 89, 255)    # #c5a059 — antique gold
GOLD_LIGHT = (240, 213, 138, 255)   # #f0d58a — lighter gold
RED        = (192, 57, 43, 255)     # #c0392b — cinematic red
SAND       = (245, 238, 219, 255)   # #f5eedb — sun-bleached sand


def draw_star(draw, cx, cy, outer_r, inner_r, points, fill, outline=None, outline_width=1):
    """Draw a multi-point star polygon."""
    import math
    coords = []
    for i in range(points * 2):
        angle = math.pi / points * i - math.pi / 2
        r = outer_r if i % 2 == 0 else inner_r
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        coords.append((x, y))
    draw.polygon(coords, fill=fill)
    if outline:
        draw.line(coords + [coords[0]], fill=outline, width=outline_width)


def create_favicon_image(size):
    """
    Create a square favicon image at the given pixel size.
    Design: dark wood background → gold badge circle → red star → gold 'W' letter
    """
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = size / 2, size / 2

    # ── Dark background circle ────────────────────────────────────────────────
    pad = size * 0.04
    draw.ellipse([pad, pad, size - pad, size - pad], fill=BG_DARK)

    # ── Gold outer ring ───────────────────────────────────────────────────────
    ring_w = max(1, size * 0.06)
    draw.ellipse([pad, pad, size - pad, size - pad],
                 outline=GOLD, width=int(ring_w))

    # ── Gold 5-point star ─────────────────────────────────────────────────────
    outer_r = size * 0.35
    inner_r = size * 0.155
    draw_star(draw, cx, cy, outer_r, inner_r, 5, fill=GOLD_LIGHT)
    # subtle red outline on the star for depth
    draw_star(draw, cx, cy, outer_r, inner_r, 5, fill=None,
              outline=GOLD, outline_width=max(1, int(size * 0.025)))

    # ── Red centre circle ─────────────────────────────────────────────────────
    cr = size * 0.18
    draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=RED)
    draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr],
                 outline=GOLD, width=max(1, int(size * 0.02)))

    # ── White 'W' letter in centre ────────────────────────────────────────────
    # Use a simple drawn 'W' so we don't depend on a specific font file
    font_size = int(size * 0.22)
    try:
        # Try loading a bold system font
        font = ImageFont.truetype("arialbd.ttf", font_size)
    except Exception:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()

    text = "W"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = cx - tw / 2
    ty = cy - th / 2 - size * 0.01

    # Tiny shadow for legibility
    draw.text((tx + 1, ty + 1), text, font=font, fill=(0, 0, 0, 180))
    draw.text((tx, ty), text, font=font, fill=(255, 249, 237, 255))

    return img


def save_png(img, path, size=None):
    if size:
        img = img.resize((size, size), Image.LANCZOS)
    img.save(str(path), "PNG", optimize=True)
    print(f"  Saved: {path}  ({path.stat().st_size:,} bytes)")


def build_ico(images_rgba):
    """
    Build a multi-size .ico file from a list of (size, PIL.Image) tuples.
    Each image is stored as a raw RGBA BMP DIB.
    """
    # ICO header: WORD(0), WORD(1=icon), WORD(count)
    num = len(images_rgba)
    header = struct.pack("<HHH", 0, 1, num)

    image_data_list = []
    for size, img in images_rgba:
        img_resized = img.resize((size, size), Image.LANCZOS)
        # Convert to 32-bit BGRA for the ICO DIB
        r, g, b, a = img_resized.split()
        bgra = Image.merge("RGBA", (b, g, r, a))
        raw = bgra.tobytes()

        # BITMAPINFOHEADER (40 bytes) + pixel data (top-down, no mask)
        # height is doubled for ICO format (image + mask), stored negative = top-down
        bih = struct.pack(
            "<IiiHHIIiiII",
            40,           # biSize
            size,         # biWidth
            size * 2,     # biHeight (doubled for ICO)
            1,            # biPlanes
            32,           # biBitCount
            0,            # biCompression (BI_RGB)
            len(raw),     # biSizeImage
            0, 0,         # biXPelsPerMeter, biYPelsPerMeter
            0, 0,         # biClrUsed, biClrImportant
        )

        # ICO stores rows bottom-up
        rows = []
        for row in range(size - 1, -1, -1):
            rows.append(raw[row * size * 4: (row + 1) * size * 4])
        dib_pixels = b"".join(rows)

        # AND mask (all zeros = fully opaque for 32-bit RGBA ICO)
        mask_row_bytes = ((size + 31) // 32) * 4
        and_mask = b"\x00" * (mask_row_bytes * size)

        dib = bih + dib_pixels + and_mask
        image_data_list.append(dib)

    # Directory entries (16 bytes each)
    DIRECTORY_SIZE = 6 + num * 16
    offset = DIRECTORY_SIZE
    directory = b""
    for (size, _), dib in zip(images_rgba, image_data_list):
        w = size if size < 256 else 0
        h = size if size < 256 else 0
        directory += struct.pack(
            "<BBBBHHII",
            w, h,           # width, height (0 = 256)
            0,              # color count (0 = no palette)
            0,              # reserved
            1,              # planes
            32,             # bit count
            len(dib),       # size of image data
            offset,         # offset of image data
        )
        offset += len(dib)

    ico_data = header + directory + b"".join(image_data_list)
    return ico_data


def main():
    if not PIL_AVAILABLE:
        print("ERROR: Pillow (PIL) is required. Install with: pip install Pillow")
        return

    print("Spaghetti Western Discovery - Favicon Generator")
    print("=" * 54)

    # Generate the base high-res image
    base = create_favicon_image(256)

    # ── apple-touch-icon.png (180×180) ────────────────────────────────────────
    atl_path = OUTPUT_DIR / "apple-touch-icon.png"
    apple = base.resize((180, 180), Image.LANCZOS)
    # Flatten alpha onto a solid dark background for iOS
    bg = Image.new("RGB", (180, 180), (26, 20, 18))
    bg.paste(apple, mask=apple.split()[3])
    bg.save(str(atl_path), "PNG", optimize=True)
    print(f"  Saved: {atl_path}  ({atl_path.stat().st_size:,} bytes)")

    # ── favicon-32x32.png ─────────────────────────────────────────────────────
    save_png(base, OUTPUT_DIR / "favicon-32x32.png", size=32)

    # ── favicon-16x16.png ─────────────────────────────────────────────────────
    save_png(base, OUTPUT_DIR / "favicon-16x16.png", size=16)

    # ── favicon.ico (multi-size: 16, 32, 48) ─────────────────────────────────
    ico_images = [(s, base) for s in (16, 32, 48)]
    ico_data = build_ico(ico_images)
    ico_path = OUTPUT_DIR / "favicon.ico"
    ico_path.write_bytes(ico_data)
    print(f"  Saved: {ico_path}  ({ico_path.stat().st_size:,} bytes)")

    print()
    print("All favicon assets generated successfully!")
    print("   Deploy these files to the root of your Cloudflare Pages site.")


if __name__ == "__main__":
    main()
