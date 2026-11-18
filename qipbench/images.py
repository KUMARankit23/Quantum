"""Image sources and classical pre-processing.

Every image that enters a quantum circuit passes through the same, explicit
chain so that each stage can be varied as an experimental factor:

    source (high-res) -> grayscale -> resize (interpolation) -> normalise -> quantise (bit depth)
"""

from __future__ import annotations

import io
from dataclasses import dataclass

import cv2
import numpy as np
from PIL import Image
from skimage import data as skdata
from skimage import exposure

SOURCE_RES = 256          # resolution at which test images are generated / loaded
REFERENCE_RES = 64        # resolution of the end-to-end reference image

INTERPOLATIONS = {
    "nearest": cv2.INTER_NEAREST,
    "bilinear": cv2.INTER_LINEAR,
    "bicubic": cv2.INTER_CUBIC,
    "area": cv2.INTER_AREA,
}
NORMALIZATIONS = ("none", "minmax", "equalize")


# --------------------------------------------------------------------------- sources

def _grid(res: int) -> tuple[np.ndarray, np.ndarray]:
    ax = (np.arange(res) + 0.5) / res
    return np.meshgrid(ax, ax)


def _synthetic(name: str, res: int) -> np.ndarray:
    x, y = _grid(res)
    if name == "gradient":
        return (x + y) / 2
    if name == "checkerboard":
        return ((np.floor(x * 4) + np.floor(y * 4)) % 2).astype(float)
    if name == "disk":
        return ((x - 0.5) ** 2 + (y - 0.5) ** 2 < 0.35 ** 2).astype(float)
    if name == "blocks":
        img = np.full((res, res), 0.1)
        img[(x > 0.1) & (x < 0.45) & (y > 0.1) & (y < 0.6)] = 0.9
        img[(x > 0.55) & (x < 0.9) & (y > 0.4) & (y < 0.9)] = 0.55
        return img
    raise KeyError(name)


def _natural(name: str) -> np.ndarray:
    if name == "camera":
        img = skdata.camera()
    elif name == "phantom":
        img = skdata.shepp_logan_phantom()
    elif name == "coins":
        img = skdata.coins()
    elif name == "moon":
        img = skdata.moon()
    else:
        raise KeyError(name)
    return to_unit_gray(img)


SYNTHETIC_IMAGES = ("gradient", "checkerboard", "disk", "blocks")
NATURAL_IMAGES = ("camera", "phantom", "coins", "moon")
STANDARD_IMAGES = NATURAL_IMAGES + SYNTHETIC_IMAGES


def load_standard(name: str, res: int = SOURCE_RES) -> np.ndarray:
    """Return a named test image as float grayscale in [0, 1] at ``res`` x ``res``."""
    if name in SYNTHETIC_IMAGES:
        return _synthetic(name, res)
    img = _natural(name)
    side = min(img.shape)                         # centre crop to square
    r0, c0 = (img.shape[0] - side) // 2, (img.shape[1] - side) // 2
    img = img[r0:r0 + side, c0:c0 + side]
    return cv2.resize(img.astype(np.float32), (res, res), interpolation=cv2.INTER_AREA).astype(float)


def to_unit_gray(img: np.ndarray) -> np.ndarray:
    """Convert any uint8/float, gray/RGB(A) array to float grayscale in [0, 1]."""
    arr = np.asarray(img)
    if arr.ndim == 3:
        arr = arr[..., :3].astype(float) @ np.array([0.299, 0.587, 0.114])   # ITU-R BT.601 luma
    arr = arr.astype(float)
    if arr.max() > 1.0:
        arr = arr / 255.0
    return np.clip(arr, 0.0, 1.0)


def load_bytes(raw: bytes, res: int = SOURCE_RES) -> np.ndarray:
    """Decode an uploaded image file and return a square float source image."""
    img = to_unit_gray(np.array(Image.open(io.BytesIO(raw)).convert("RGB")))
    side = min(img.shape)
    r0, c0 = (img.shape[0] - side) // 2, (img.shape[1] - side) // 2
    img = img[r0:r0 + side, c0:c0 + side]
    return cv2.resize(img.astype(np.float32), (res, res), interpolation=cv2.INTER_AREA).astype(float)


# --------------------------------------------------------------------------- preprocessing

@dataclass(frozen=True)
class Preprocessed:
    resized: np.ndarray      # after interpolation, before normalisation
    normalized: np.ndarray   # after normalisation, continuous in [0, 1]
    quantized: np.ndarray    # after quantisation, what is loaded into the circuit (float in [0, 1])
    levels: np.ndarray       # integer grey levels in [0, 2^bit_depth - 1]
    reference: np.ndarray    # source at REFERENCE_RES for end-to-end comparison


def resize(img: np.ndarray, size: int, interpolation: str = "area") -> np.ndarray:
    if interpolation not in INTERPOLATIONS:
        raise ValueError(f"interpolation must be one of {list(INTERPOLATIONS)}")
    out = cv2.resize(img.astype(np.float32), (size, size), interpolation=INTERPOLATIONS[interpolation])
    return np.clip(out.astype(float), 0.0, 1.0)


def normalize(img: np.ndarray, method: str = "minmax") -> np.ndarray:
    if method == "none":
        return img.copy()
    if method == "minmax":
        lo, hi = img.min(), img.max()
        return np.zeros_like(img) if hi - lo < 1e-12 else (img - lo) / (hi - lo)
    if method == "equalize":
        if img.max() - img.min() < 1e-12:
            return np.zeros_like(img)
        return exposure.equalize_hist(img, nbins=256)
    raise ValueError(f"normalization must be one of {NORMALIZATIONS}")


def quantize(img: np.ndarray, bit_depth: int) -> tuple[np.ndarray, np.ndarray]:
    """Uniform scalar quantisation to 2^bit_depth grey levels."""
    if not 1 <= bit_depth <= 16:
        raise ValueError("bit_depth must be in [1, 16]")
    top = 2 ** bit_depth - 1
    levels = np.rint(np.clip(img, 0, 1) * top).astype(int)
    return levels / top, levels


def preprocess(source: np.ndarray, size: int, interpolation: str = "area",
               normalization: str = "minmax", bit_depth: int = 8) -> Preprocessed:
    if size < 2 or size & (size - 1):
        raise ValueError("size must be a power of two >= 2 (each pixel index maps onto qubits)")
    resized = resize(source, size, interpolation)
    normalized = normalize(resized, normalization)
    quantized, levels = quantize(normalized, bit_depth)
    reference = normalize(resize(source, REFERENCE_RES, "area"), "minmax")
    return Preprocessed(resized, normalized, quantized, levels, reference)


def upsample(img: np.ndarray, res: int = REFERENCE_RES) -> np.ndarray:
    """Bilinear post-processing used to compare small reconstructions with the reference."""
    return resize(img, res, "bilinear")
