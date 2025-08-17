from PIL import Image, ImageFont, ImageDraw
from typing import Optional, Tuple
import math, textwrap, os

DEFAULT_FONT_CANDIDATES = [
    "app/assets/fonts/Inter-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/Library/Fonts/Arial.ttf",
    "C:/Windows/Fonts/arial.ttf",
]


def ensure_rgba(img: Image.Image) -> Image.Image:
    if img.mode != "RGBA":
        return img.convert("RGBA")
    return img


def pick_font_path(explicit: Optional[str] = None) -> Optional[str]:
    if explicit and os.path.exists(explicit):
        return explicit
    for p in DEFAULT_FONT_CANDIDATES:
        if os.path.exists(p):
            return p
    return None


def auto_font(font_path: Optional[str], requested_px: int, img_w: int, img_h: int) -> ImageFont.FreeTypeFont:
    path = pick_font_path(font_path)

    # Determine size: if requested_px == 0 -> auto scale to ~10% of min dimension, clamped.
    if requested_px and requested_px > 0:
        size = requested_px
    else:
        base = int(0.10 * min(img_w, img_h))
        size = max(14, min(base, 128))

    if path:
        return ImageFont.truetype(path, size=size)
    else:
        return ImageFont.load_default()


def _wrap_text_to_fit(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> str:
    if not text:
        return ""
    # Try dynamic wrap: decrease width until fits by measuring each line
    words = text.split()
    if not words:
        return text

    # Start with a rough max chars per line
    # We'll refine by measuring pixel width
    for width_chars in range(max(8, len(text)), 0, -1):
        candidate = textwrap.fill(text, width=width_chars)
        lines = candidate.splitlines()
        if all(draw.textlength(line, font=font) <= max_width for line in lines):
            return candidate
    return text


def draw_centered_multiline(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, img_w: int, img_h: int, fill: str = "#000000"):
    if not text:
        return
    margin = int(0.10 * img_w)
    max_line_width = img_w - 2 * margin

    wrapped = _wrap_text_to_fit(draw, text, font, max_line_width)

    # Measure total text block size
    lines = wrapped.splitlines()
    line_heights = []
    line_widths = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        line_widths.append(w)
        line_heights.append(h)

    line_spacing = max(4, int(0.25 * (line_heights[0] if line_heights else 0)))
    total_h = sum(line_heights) + line_spacing * (len(lines) - 1)

    y = (img_h - total_h) // 2
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        x = (img_w - w) // 2
        draw.text((x, y), line, font=font, fill=fill)
        y += h + line_spacing
