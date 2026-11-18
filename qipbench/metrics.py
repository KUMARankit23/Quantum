"""Quality, distribution and edge-map metrics.

Images are float arrays in [0, 1], so PSNR uses a peak of 1.0. A perfect reconstruction
has infinite PSNR; it is capped at PSNR_CAP so that averages and effect sizes stay finite.
"""

from __future__ import annotations

import numpy as np
from skimage.metrics import structural_similarity

PSNR_CAP = 60.0


def mse(ref: np.ndarray, img: np.ndarray) -> float:
    return float(np.mean((np.asarray(ref, float) - np.asarray(img, float)) ** 2))


def psnr(ref: np.ndarray, img: np.ndarray) -> float:
    e = mse(ref, img)
    return PSNR_CAP if e <= 10 ** (-PSNR_CAP / 10) else float(10 * np.log10(1.0 / e))


def ssim(ref: np.ndarray, img: np.ndarray) -> float:
    """Windowed SSIM; images smaller than the 3x3 minimum window use the global SSIM formula."""
    ref, img = np.asarray(ref, float), np.asarray(img, float)
    side = min(ref.shape)
    if side >= 3:
        win = min(7, side if side % 2 else side - 1)
        return float(structural_similarity(ref, img, data_range=1.0, win_size=win))
    c1, c2 = 0.01 ** 2, 0.03 ** 2
    mx, my = ref.mean(), img.mean()
    vx, vy = ref.var(), img.var()
    cov = ((ref - mx) * (img - my)).mean()
    return float(((2 * mx * my + c1) * (2 * cov + c2)) / ((mx ** 2 + my ** 2 + c1) * (vx + vy + c2)))


def level_accuracy(ref: np.ndarray, img: np.ndarray, bit_depth: int) -> float:
    """Fraction of pixels recovered at exactly the right grey level."""
    top = 2 ** bit_depth - 1
    return float(np.mean(np.rint(ref * top) == np.rint(img * top)))


def classical_fidelity(p: np.ndarray, q: np.ndarray) -> float:
    """Bhattacharyya fidelity (Σ √(p_i q_i))² between ideal and measured outcome distributions."""
    p = p / max(p.sum(), 1e-300)
    q = q / max(q.sum(), 1e-300)
    return float(np.sum(np.sqrt(p * q)) ** 2)


def tvd(p: np.ndarray, q: np.ndarray) -> float:
    p = p / max(p.sum(), 1e-300)
    q = q / max(q.sum(), 1e-300)
    return float(0.5 * np.abs(p - q).sum())


def edge_scores(truth: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    t, p = truth.astype(bool), pred.astype(bool)
    tp = float((t & p).sum())
    fp = float((~t & p).sum())
    fn = float((t & ~p).sum())
    precision = tp / (tp + fp) if tp + fp else float(not t.any())
    recall = tp / (tp + fn) if tp + fn else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    union = tp + fp + fn
    return {"precision": precision, "recall": recall, "f1": f1,
            "iou": tp / union if union else 1.0, "pixel_accuracy": float((t == p).mean())}


def image_entropy(img: np.ndarray, bins: int = 256) -> float:
    """Shannon entropy (bits) of the grey-level histogram, a proxy for image complexity."""
    hist, _ = np.histogram(img, bins=bins, range=(0, 1))
    p = hist[hist > 0] / hist.sum()
    return float(-(p * np.log2(p)).sum())
