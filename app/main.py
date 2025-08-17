from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import Response, HTMLResponse
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from typing import Optional

from .utils import ensure_rgba, auto_font

app = FastAPI(title="Watermark API", version="1.0.0")

@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <html>
      <head><title>Watermark API</title></head>
      <body style='font-family: sans-serif;'>
        <h2>Watermark API</h2>
        <p>POST <code>/watermark</code> with an image file and fields to get the processed image.</p>
        <pre>
        curl -s -X POST \
          -F "file=@/path/to/image.jpg" \
          -F "text=Your watermark here" \
          -F "opacity=200" \
          -F "text_color=#000000" \
          -F "font_size=0" \
          http://localhost:8000/watermark > out.png
        </pre>
      </body>
    </html>
    """

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/watermark")
async def watermark(
    file: UploadFile = File(...),
    text: str = Form(""),
    opacity: int = Form(200),  # 0..255
    text_color: str = Form("#000000"),
    font_size: int = Form(0),  # 0 = auto
    font_path: Optional[str] = Form(None),
    output: str = Form("png"),  # png|jpg|jpeg|webp
):
    try:
        content = await file.read()
        base = Image.open(BytesIO(content))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image upload")

    img = ensure_rgba(base)
    w, h = img.size

    # Draw centered text with background
    draw = ImageDraw.Draw(img)
    font = auto_font(font_path=font_path, requested_px=font_size, img_w=w, img_h=h)

    # text size
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_w = text_bbox[2] - text_bbox[0]
    text_h = text_bbox[3] - text_bbox[1]

    # center position
    x = (w - text_w) // 2
    y = (h - text_h) // 2

    # bg
    padding = 20
    rect = Image.new("RGBA", (text_w + 2 * padding, text_h + 2 * padding), (255, 255, 255, opacity))
    img.alpha_composite(rect, dest=(x - padding, y - padding))

    # text
    draw.text((x, y), text, font=font, fill=text_color)

    # Encode result
    fmt = output.upper()
    if fmt == "JPG":
        fmt = "JPEG"

    out = BytesIO()
    save_img = img
    if fmt in ("JPEG", "JPG"):
        save_img = img.convert("RGB")
        save_img.save(out, fmt, quality=95, optimize=True)
    elif fmt == "PNG":
        save_img.save(out, fmt, optimize=True)
    elif fmt == "WEBP":
        save_img.save(out, fmt, quality=95, method=6)
    else:
        raise HTTPException(status_code=400, detail="Unsupported output format")

    headers = {"Content-Disposition": f"inline; filename=watermarked.{output.lower()}"}
    media = {
        "PNG": "image/png",
        "JPEG": "image/jpeg",
        "WEBP": "image/webp",
    }[fmt]

    return Response(content=out.getvalue(), media_type=media, headers=headers)

