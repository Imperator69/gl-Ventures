#!/usr/bin/env python3
"""Regenerate raster icons and the social preview image in src/static (needs Pillow).

    python3 tools/make_images.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "src" / "static"
NAVY = (9, 17, 29)
BRASS = (216, 180, 124)
FONT_DIRS = ["/usr/share/fonts/opentype/inter", "/usr/share/fonts/truetype/inter"]


def font(name, size):
    for d in FONT_DIRS:
        p = Path(d) / name
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.truetype("DejaVuSans-Bold.ttf", size)


def icon(size):
    scale = 4
    s = size * scale
    img = Image.new("RGB", (s, s), NAVY)
    d = ImageDraw.Draw(img)
    pad, w = round(s * 0.14), max(2, round(s * 0.04))
    d.rounded_rectangle([pad, pad, s - pad, s - pad], radius=round(s * 0.14), outline=BRASS, width=w)
    f = font("InterDisplay-Bold.otf", round(s * 0.36))
    d.text((s / 2, s / 2 + s * 0.01), "GL", font=f, fill="white", anchor="mm")
    return img.resize((size, size), Image.LANCZOS)


def og_image():
    W, H = 1200, 630
    hero = Image.open(STATIC / "assets" / "hero-1672.webp").convert("RGB")
    ratio = max(W / hero.width, H / hero.height)
    hero = hero.resize((round(hero.width * ratio), round(hero.height * ratio)), Image.LANCZOS)
    x = hero.width - W
    img = hero.crop((x, 0, x + W, H))
    shade = Image.new("L", (W, 1))
    for i in range(W):
        shade.putpixel((i, 0), int(245 - 170 * (i / W)))
    shade = shade.resize((W, H))
    img = Image.composite(Image.new("RGB", (W, H), NAVY), img, shade)
    d = ImageDraw.Draw(img)
    m = 80
    d.rounded_rectangle([m, 78, m + 62, 140], radius=12, outline="white", width=3)
    d.text((m + 31, 110), "GL", font=font("InterDisplay-Bold.otf", 28), fill="white", anchor="mm")
    d.text((m + 84, 110), "V E N T U R E S", font=font("InterDisplay-SemiBold.otf", 26), fill="white", anchor="lm")
    d.text((m, 270), "Komplexe Vorhaben.", font=font("InterDisplay-SemiBold.otf", 76), fill="white", anchor="ls")
    d.text((m, 360), "Klare Umsetzung.", font=font("InterDisplay-SemiBold.otf", 76), fill=(166, 179, 198), anchor="ls")
    d.text((m, 470), "Complex Services · Strategic Advisory · Venture Building", font=font("InterDisplay-Medium.otf", 28), fill=BRASS, anchor="ls")
    d.text((m, 540), "Wien · Vienna, Austria · gl-ventures.at", font=font("InterDisplay-Regular.otf", 24), fill=(200, 208, 220), anchor="ls")
    img.save(STATIC / "assets" / "og-image.jpg", quality=86, optimize=True, progressive=True)


def main():
    icon(180).save(STATIC / "apple-touch-icon.png", optimize=True)
    icon(512).save(STATIC / "assets" / "logo-512.png", optimize=True)
    icon(48).save(STATIC / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    og_image()
    print("Images written to src/static")


if __name__ == "__main__":
    main()
