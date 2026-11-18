"""FastAPI service behind the QIP-Bench dashboard.

    GET  /                      dashboard (web/index.html)
    GET  /api/meta              available options and baselines
    POST /api/pipeline          run one quantum image pipeline (optional uploaded image)
    POST /api/compare           FRQI vs NEQR vs amplitude on the same input
    POST /api/edges             quantum Hadamard edge detection vs classical
    GET  /api/results           experiment summary (results/summary.json)
    GET  /figures/<name>        generated research figures
"""

from __future__ import annotations

import base64
import io
import json
import warnings
from pathlib import Path

import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from matplotlib import colormaps
from PIL import Image

from . import __version__, edge, images
from .encoders import ENCODERS, get_encoder
from .pipeline import PipelineConfig, run
from .studies import FACTOR_LABELS, NOISELESS_BASE, NOISY_BASE

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
RESULTS = ROOT / "results"

MAX_QUBITS_EXACT = 18        # statevector of 2^18 amplitudes is instant
MAX_QUBITS_NOISY = 12        # trajectory simulation beyond this takes minutes per run

app = FastAPI(title="QIP-Bench", version=__version__,
              description="Performance-factor analysis for quantum image processing")
app.mount("/static", StaticFiles(directory=WEB), name="static")
if (RESULTS / "figures").exists():
    app.mount("/figures", StaticFiles(directory=RESULTS / "figures"), name="figures")


# ---------------------------------------------------------------- helpers

def png(img: np.ndarray, cmap: str | None = None, scale: int = 256) -> str:
    arr = np.clip(np.asarray(img, float), 0, 1)
    if cmap:
        rgb = (colormaps[cmap](arr)[..., :3] * 255).astype(np.uint8)
        pil = Image.fromarray(rgb)
    else:
        pil = Image.fromarray((arr * 255).round().astype(np.uint8), mode="L")
    pil = pil.resize((scale, scale), Image.NEAREST)
    buf = io.BytesIO()
    pil.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def _source(file: UploadFile | None, image: str) -> np.ndarray:
    if file is not None and file.filename:
        raw = file.file.read()
        if len(raw) > 10 * 2 ** 20:
            raise HTTPException(413, "image larger than 10 MB")
        try:
            return images.load_bytes(raw)
        except Exception as exc:  # noqa: BLE001 - any decoder failure is a bad upload
            raise HTTPException(400, f"could not decode image: {exc}") from exc
    if image not in images.STANDARD_IMAGES:
        raise HTTPException(400, f"unknown image '{image}'")
    return images.load_standard(image)


def _guard(cfg: PipelineConfig) -> None:
    if cfg.size not in (2, 4, 8, 16, 32):
        raise HTTPException(400, "size must be 2, 4, 8, 16 or 32")
    q = get_encoder(cfg.encoding).n_qubits((cfg.size, cfg.size), cfg.bit_depth, cfg.structure)
    if q > MAX_QUBITS_EXACT:
        raise HTTPException(400, f"{cfg.encoding.upper()} needs {q} qubits here; the live lab allows "
                                 f"{MAX_QUBITS_EXACT}. Reduce size or bit depth.")
    if cfg.noise > 0 and q > MAX_QUBITS_NOISY:
        raise HTTPException(400, f"noisy simulation of {q} qubits is too slow for the live lab "
                                 f"(limit {MAX_QUBITS_NOISY}). Use a 4x4 image or fewer bits.")
    if cfg.encoding == "amplitude" and cfg.operations:
        raise HTTPException(400, "inversion is not a unitary on amplitude-encoded images")
    if cfg.structure == "baseline" and cfg.size > 16:
        raise HTTPException(400, "baseline (naive) circuits are limited to 16x16")


def _config(encoding, image, size, bit_depth, interpolation, normalization, structure,
            opt_level, operations, shots, noise, estimator, fill, seed) -> PipelineConfig:
    try:
        return PipelineConfig(encoding=encoding, image=image, size=size, bit_depth=bit_depth,
                              interpolation=interpolation, normalization=normalization,
                              structure=structure, opt_level=opt_level, operations=operations,
                              shots=None if shots <= 0 else shots, noise=noise,
                              estimator=estimator, fill=fill, seed=seed)
    except (TypeError, ValueError) as exc:
        raise HTTPException(400, str(exc)) from exc


def _circuit_text(qc) -> str | None:
    if qc.num_qubits > 9 or qc.size() > 70:
        return None
    with warnings.catch_warnings():          # Windows console charset warning; output is UTF-8 JSON anyway
        warnings.simplefilter("ignore", RuntimeWarning)
        return str(qc.draw("text", fold=-1))


def _measurement(r) -> dict:
    """Sparse outcome record so the browser can replay the shots and rebuild the image live."""
    dist = r.distribution
    idx = np.flatnonzero(dist)
    if idx.size > 20000:                      # keep payloads small: drop the rarest outcomes
        idx = idx[np.argsort(dist[idx])[-20000:]]
    return {"exact": r.config.shots is None, "shots": r.config.shots or 0, "layout": r.layout,
            "index": idx.tolist(), "weight": np.round(dist[idx], 10).tolist()}


def _pipeline_payload(r) -> dict:
    err = np.abs(r.expected - r.reconstructed)
    return {
        "config": {**r.config.__dict__},
        "metrics": r.metrics,
        "images": {
            "source": png(images.resize(r.source, 256, "area")),
            "preprocessed": png(r.preprocessed.quantized),
            "expected": png(r.expected),
            "reconstructed": png(r.reconstructed),
            "error": png(err / max(err.max(), 1e-9) if err.max() > 1e-9 else err, "magma"),
        },
        "pixels": {"loaded": np.round(r.preprocessed.quantized, 4).tolist(),
                   "expected": np.round(r.expected, 4).tolist(),
                   "reconstructed": np.round(r.reconstructed, 4).tolist()},
        "measurement": _measurement(r),
        "circuit": _circuit_text(r.circuit),
        "max_error": float(err.max()),
    }


def _run_or_400(cfg: PipelineConfig, source: np.ndarray):
    try:
        return run(cfg, source)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


# ---------------------------------------------------------------- routes

@app.get("/", include_in_schema=False)
def index():
    return FileResponse(WEB / "index.html")


@app.get("/api/meta")
def meta():
    return {
        "version": __version__,
        "encodings": {k: {"estimators": list(v.estimators)} for k, v in ENCODERS.items()},
        "images": list(images.STANDARD_IMAGES),
        "interpolations": list(images.INTERPOLATIONS),
        "normalizations": list(images.NORMALIZATIONS),
        "factors": FACTOR_LABELS,
        "baselines": {"noiseless": NOISELESS_BASE.__dict__, "noisy": NOISY_BASE.__dict__},
        "has_results": (RESULTS / "summary.json").exists(),
    }


@app.post("/api/pipeline")
def pipeline(file: UploadFile | None = File(None), image: str = Form("camera"), encoding: str = Form("frqi"),
             size: int = Form(8), bit_depth: int = Form(8), interpolation: str = Form("area"),
             normalization: str = Form("minmax"), structure: str = Form("optimized"),
             opt_level: int = Form(1), operations: int = Form(0), shots: int = Form(4096),
             noise: float = Form(0.0), estimator: str = Form("auto"), fill: str = Form("neighbor"),
             seed: int = Form(0)):
    cfg = _config(encoding, image, size, bit_depth, interpolation, normalization, structure,
                  opt_level, operations, shots, noise, estimator, fill, seed)
    _guard(cfg)
    return _pipeline_payload(_run_or_400(cfg, _source(file, image)))


@app.post("/api/compare")
def compare(file: UploadFile | None = File(None), image: str = Form("camera"), size: int = Form(4),
            bit_depth: int = Form(8), shots: int = Form(4096), noise: float = Form(0.0),
            structure: str = Form("optimized"), seed: int = Form(0)):
    source = _source(file, image)
    out = {}
    for enc in ENCODERS:
        cfg = _config(enc, image, size, bit_depth, "area", "minmax", structure, 1, 0, shots, noise,
                      "auto", "neighbor", seed)
        try:
            _guard(cfg)
        except HTTPException as exc:
            out[enc] = {"error": exc.detail}
            continue
        r = _run_or_400(cfg, source)
        out[enc] = {"metrics": r.metrics, "reconstructed": png(r.reconstructed),
                    "error_map": png(np.abs(r.expected - r.reconstructed), "magma")}
    first = images.preprocess(source, size, "area", "minmax", bit_depth)
    return {"expected": png(first.quantized), "results": out}


@app.post("/api/edges")
def edges(file: UploadFile | None = File(None), image: str = Form("blocks"), size: int = Form(16),
          shots: int = Form(16384), noise: float = Form(0.0), threshold: float = Form(0.2), seed: int = Form(0)):
    if size not in (4, 8, 16, 32):
        raise HTTPException(400, "size must be 4, 8, 16 or 32")
    if noise > 0 and size > 8:
        raise HTTPException(400, "noisy QHED is limited to 8x8 in the live lab")
    img = images.preprocess(_source(file, image), size).quantized
    r = edge.detect(img, threshold, None if shots <= 0 else shots, noise, seed=seed)
    mag_scale = max(r.classical_magnitude.max(), 1e-9)
    return {
        "metrics": r.metrics,
        "images": {
            "input": png(img),
            "quantum_gradient": png(r.magnitude / mag_scale, "magma"),
            "classical_gradient": png(r.classical_magnitude / mag_scale, "magma"),
            "quantum_edges": png(r.edges.astype(float)),
            "classical_edges": png(r.classical_edges.astype(float)),
            "sobel_edges": png(r.sobel_edges.astype(float)),
        },
    }


@app.get("/api/findings")
def findings():
    """Numbered key findings from results/REPORT.md, as plain strings."""
    path = RESULTS / "REPORT.md"
    if not path.exists():
        return {"findings": []}
    text = path.read_text(encoding="utf-8")
    section = text.split("## 2. Key findings", 1)[-1].split("\n## ", 1)[0]
    items = [ln.split(". ", 1)[1] for ln in section.splitlines() if ln[:1].isdigit() and ". " in ln]
    return {"findings": items}


@app.get("/api/results")
def results():
    path = RESULTS / "summary.json"
    if not path.exists():
        raise HTTPException(404, "no results yet - run `python -m qipbench run`")
    return json.loads(path.read_text())
