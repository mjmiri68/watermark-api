Adds a white overlay over the whole image and centers your custom text.

## Run locally
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

Examples
curl -s -X POST \
  -F "file=@/path/to/input.jpg" \
  -F "text=My Store — Summer Sale" \
  http://localhost:8000/watermark > out.png

Stronger overlay, custom color text, JPG output:
curl -s -X POST \
  -F "file=@/path/to/input.jpg" \
  -F "text=CONFIDENTIAL" \
  -F "opacity=235" \
  -F "text_color=#111111" \
  -F "output=jpg" \
  http://localhost:8000/watermark > out.jpg

Explicit font and size:
curl -s -X POST \
  -F "file=@/path/to/input.jpg" \
  -F "text=Special Offer" \
  -F "font_path=app/assets/fonts/Inter-Regular.ttf" \
  -F "font_size=72" \
  http://localhost:8000/watermark > out.png
