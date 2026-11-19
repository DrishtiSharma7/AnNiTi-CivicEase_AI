"""Local, rules-first analysis that runs BEFORE any model call (optional deps: Pillow, pytesseract, pypdf).
Everything degrades gracefully when a library is missing."""
import io
import re
from typing import Optional

AADHAAR_RX = re.compile(r"(?<!\d)(\d{4}[\s-]?\d{4}[\s-]?\d{4})(?!\d)")
BLUR_THRESHOLD = 40.0   # variance of edge response; tune on your synthetic set
MIN_SIDE = 400


def image_quality(data: bytes) -> Optional[str]:
    """'blurry' if the image is too small or too soft, 'clear' otherwise, None when it cannot be judged."""
    try:
        from PIL import Image, ImageFilter, ImageStat
        img = Image.open(io.BytesIO(data)).convert("L")
        if min(img.size) < MIN_SIDE:
            return "blurry"
        score = ImageStat.Stat(img.filter(ImageFilter.FIND_EDGES)).var[0]
        return "blurry" if score < BLUR_THRESHOLD else "clear"
    except Exception:
        return None


def compress_image(data: bytes, mime: str, max_side: int = 1600) -> tuple:
    """Downscale before sending to a model (saves quota). Returns (bytes, mime)."""
    if not mime.startswith("image/"):
        return data, mime
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(data)).convert("RGB")
        img.thumbnail((max_side, max_side))
        out = io.BytesIO()
        img.save(out, "JPEG", quality=80)
        return out.getvalue(), "image/jpeg"
    except Exception:
        return data, mime


def extract_text(data: bytes, mime: str) -> Optional[str]:
    """Local OCR (images) or text layer (PDF). None when unavailable."""
    try:
        if mime == "application/pdf":
            from pypdf import PdfReader
            text = "\n".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(data)).pages)
            return text.strip() or None
        import pytesseract
        from PIL import Image
        text = pytesseract.image_to_string(Image.open(io.BytesIO(data)), lang="eng+hin")
        return text.strip() or None
    except Exception:
        return None


def find_aadhaar(text: str) -> Optional[str]:
    m = AADHAAR_RX.search(text)
    return m.group(1) if m else None
