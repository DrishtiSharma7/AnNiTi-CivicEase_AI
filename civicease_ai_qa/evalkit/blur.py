"""Proposed replacement for the backend's local blur check (see defect D007).
The backend compares edge variance with a fixed number, which depends on how much text a page has. This ratio compares an
image with a slightly blurred copy of itself: sharp images change a lot, already-blurry ones barely change.
On the synthetic set: clear 4.5-5.1, low-res 1.6-1.7, blurred 1.0. A threshold of 2.0 separates them."""
from PIL import Image, ImageFilter, ImageStat

THRESHOLD = 2.0


def _edge_var(img) -> float:
    return ImageStat.Stat(img.filter(ImageFilter.FIND_EDGES)).var[0]


def sharpness_ratio(img: Image.Image) -> float:
    g = img.convert("L")
    return _edge_var(g) / max(_edge_var(g.filter(ImageFilter.GaussianBlur(2))), 1e-6)


def looks_blurry(img: Image.Image) -> bool:
    return sharpness_ratio(img) < THRESHOLD
