"""Controlled experiments: which design factors determine QIP performance?

Two complementary designs are run:

1. One-factor-at-a-time (OFAT) sweeps.  Every factor is varied over a wide range while all
   others are held at a baseline, giving response curves (how much, and in which shape).
2. A full 2^7 factorial screening per encoding.  Seven factors at a low/high level are crossed
   so main effects AND two-factor interactions can be separated (which factor matters most,
   and which factors amplify each other).

Two baselines are used because noisy (trajectory) simulation cost grows with
2^qubits x gates x shots: noiseless studies run at 8x8, noisy studies at 4x4 (the
"small-scale" regime the problem statement targets).
"""

from __future__ import annotations

import os
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from itertools import product

import pandas as pd

from . import edge, images
from .pipeline import PipelineConfig, run

STUDY_IMAGES = ("camera", "phantom", "blocks")       # natural photo, medical phantom, synthetic
SEEDS = (0, 1, 2)

NOISELESS_BASE = PipelineConfig(size=8, bit_depth=8, shots=4096, noise=0.0)
NOISY_BASE = PipelineConfig(size=4, bit_depth=4, shots=4096, noise=1e-3)

FACTOR_LABELS = {
    "size": "Image size",
    "bit_depth": "Intensity bit depth",
    "interpolation": "Resize interpolation",
    "normalization": "Intensity normalisation",
    "structure": "Circuit structure",
    "opt_level": "Transpiler optimisation",
    "operations": "Number of operations",
    "shots": "Measurement shots",
    "noise": "Hardware noise",
    "estimator": "Reconstruction estimator",
    "fill": "Missing-pixel fill",
    "image": "Image content",
    "encoding": "Encoding method",
}


@dataclass
class Study:
    name: str
    factor: str
    levels: list | dict              # dict -> encoding-specific levels
    base: PipelineConfig
    encodings: tuple = ("frqi", "neqr")
    images: tuple = STUDY_IMAGES
    seeds: tuple = SEEDS
    overrides: dict = field(default_factory=dict)
    question: str = ""

    def configs(self) -> list[PipelineConfig]:
        out = []
        for enc in self.encodings:
            levels = self.levels[enc] if isinstance(self.levels, dict) else self.levels
            for level, img, seed in product(levels, self.images, self.seeds):
                kw = {**self.overrides, "encoding": enc, "seed": seed, self.factor: level}
                if self.factor != "image":
                    kw["image"] = img
                out.append(self.base.with_(**kw))
        return list(dict.fromkeys(out))      # image-study duplicates collapse


OFAT_STUDIES = [
    Study("image_size", "size", [2, 4, 8, 16], NOISELESS_BASE, ("frqi", "neqr", "amplitude"),
          question="How do qubits, gates and sampling demand scale with resolution?"),
    Study("bit_depth", "bit_depth", [1, 2, 4, 6, 8], NOISELESS_BASE,
          question="What does finer intensity representation cost and buy?"),
    Study("interpolation", "interpolation", ["nearest", "bilinear", "bicubic", "area"], NOISELESS_BASE,
          question="Does the classical down-sampling method change end-to-end quality?"),
    Study("normalization", "normalization", ["none", "minmax", "equalize"], NOISELESS_BASE,
          question="Does intensity normalisation help the quantum channel or the end result?"),
    Study("structure", "structure", ["baseline", "optimized"], NOISY_BASE,
          question="Same quantum state, different decomposition: how much does structure matter under noise?"),
    Study("opt_level", "opt_level", [0, 1, 2, 3], NOISY_BASE,
          question="How much can the compiler recover from a naive circuit?"),
    Study("operations", "operations", [0, 1, 2, 4, 8], NOISY_BASE,
          question="How does error accumulate with the number of processing stages?"),
    Study("shots", "shots", [64, 256, 1024, 4096, 16384, None], NOISELESS_BASE,
          question="How many measurements are needed to read an image back?"),
    Study("noise", "noise", [0.0, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2], NOISY_BASE,
          question="How quickly does each representation degrade with hardware error?"),
    Study("estimator", "estimator", {"frqi": ["conditional", "marginal"], "neqr": ["majority", "mean"]},
          NOISY_BASE, question="Can smarter classical reconstruction compensate for noise?"),
    Study("fill", "fill", ["zero", "neighbor"], NOISELESS_BASE, overrides={"shots": 256},
          question="How should pixels that were never measured be filled?"),
    Study("image", "image", list(images.STANDARD_IMAGES), NOISELESS_BASE, overrides={"shots": 1024},
          question="Does image content (complexity) change achievable quality?"),
]

# ---------------------------------------------------------------- factorial screening (coded -1 / +1)
FACTORIAL_FACTORS = {
    "frqi": {
        "size": (4, 8), "bit_depth": (2, 8), "shots": (256, 8192), "noise": (0.0, 2e-3),
        "structure": ("baseline", "optimized"), "opt_level": (0, 3), "operations": (0, 4),
    },
    "neqr": {
        "size": (2, 4), "bit_depth": (2, 4), "shots": (256, 8192), "noise": (0.0, 2e-3),
        "structure": ("baseline", "optimized"), "opt_level": (0, 3), "operations": (0, 4),
    },
}
FACTORIAL_IMAGES = STUDY_IMAGES
FACTORIAL_SEEDS = (0, 1)


def factorial_configs(encoding: str, images_=FACTORIAL_IMAGES, seeds=FACTORIAL_SEEDS) -> list[PipelineConfig]:
    factors = FACTORIAL_FACTORS[encoding]
    names = list(factors)
    out = []
    for coded in product((0, 1), repeat=len(names)):
        kw = {n: factors[n][c] for n, c in zip(names, coded)}
        for img, seed in product(images_, seeds):
            out.append(NOISY_BASE.with_(encoding=encoding, image=img, seed=seed, **kw))
    return out


# ---------------------------------------------------------------- edge-detection study (QHED)
EDGE_SWEEPS = {
    "shots": [256, 1024, 4096, 16384, 65536, None],
    "size": [4, 8, 16, 32],
    "noise": [0.0, 1e-4, 1e-3, 3e-3],
    "threshold": [0.05, 0.1, 0.2, 0.3, 0.4],
}
EDGE_BASE = {"size": 16, "shots": 16384, "noise": 0.0, "threshold": 0.2}
EDGE_IMAGES = ("blocks", "phantom", "camera")


def _edge_job(args: tuple) -> dict:
    sweep, level, img_name, seed = args
    p = {**EDGE_BASE, sweep: level}
    if p["noise"] > 0:
        p["size"] = min(p["size"], 8)                 # noisy trajectories: keep it tractable
    img = images.preprocess(images.load_standard(img_name), p["size"]).quantized
    r = edge.detect(img, p["threshold"], p["shots"], p["noise"], seed=seed)
    return {"study": f"edge_{sweep}", "factor": sweep, "level": "exact" if level is None else level,
            "image": img_name, "seed": seed, **{k: v for k, v in p.items() if k != sweep},
            **r.metrics}


def edge_jobs(seeds=SEEDS) -> list[tuple]:
    return [(s, lv, img, sd) for s, lvls in EDGE_SWEEPS.items() for lv in lvls
            for img in EDGE_IMAGES for sd in seeds]


# ---------------------------------------------------------------- runner

def _init_worker():
    from . import backend
    backend.AER_THREADS = 1


def _pipeline_job(args: tuple) -> dict:
    study, factor, cfg = args
    r = run(cfg).row()
    level = getattr(cfg, factor, "")
    if factor == "shots" and cfg.shots is None:
        level = "exact"
    return {"study": study, "factor": factor, "level": level, **r}


def _parallel(fn, jobs, workers, label, log):
    rows, t0 = [], time.perf_counter()
    if workers <= 1:
        _init_worker()
        it = map(fn, jobs)
    else:
        pool = ProcessPoolExecutor(workers, initializer=_init_worker)
        it = pool.map(fn, jobs, chunksize=1)
    for i, row in enumerate(it, 1):
        rows.append(row)
        if log and (i % max(1, len(jobs) // 10) == 0 or i == len(jobs)):
            log(f"  {label}: {i}/{len(jobs)} runs  ({time.perf_counter() - t0:.0f}s)")
    if workers > 1:
        pool.shutdown()
    return rows


def run_ofat(studies=None, workers: int | None = None, quick: bool = False, log=print) -> pd.DataFrame:
    studies = studies or OFAT_STUDIES
    jobs = []
    for st in studies:
        if quick:
            st = Study(**{**st.__dict__, "images": st.images[:1], "seeds": st.seeds[:1]})
        jobs += [(st.name, st.factor, c) for c in st.configs()]
    return pd.DataFrame(_parallel(_pipeline_job, jobs, workers or _workers(), "OFAT", log))


def run_factorial(workers: int | None = None, quick: bool = False, log=print) -> pd.DataFrame:
    jobs = []
    for enc in FACTORIAL_FACTORS:
        imgs, seeds = (FACTORIAL_IMAGES[:1], FACTORIAL_SEEDS[:1]) if quick else (FACTORIAL_IMAGES, FACTORIAL_SEEDS)
        jobs += [("factorial", "factorial", c) for c in factorial_configs(enc, imgs, seeds)]
    return pd.DataFrame(_parallel(_pipeline_job, jobs, workers or _workers(), "factorial", log))


def run_edges(workers: int | None = None, quick: bool = False, log=print) -> pd.DataFrame:
    jobs = edge_jobs(SEEDS[:1] if quick else SEEDS)
    if quick:
        jobs = [j for j in jobs if j[2] == EDGE_IMAGES[0]]
    return pd.DataFrame(_parallel(_edge_job, jobs, workers or _workers(), "edges", log))


def _workers() -> int:
    """CPU-bound workers, capped by memory: each process holds Qiskit + Aer (~400 MB)."""
    cpu = max(1, (os.cpu_count() or 2) - 2)
    try:
        import psutil
        mem = int(psutil.virtual_memory().available / 2 ** 30 / 0.6)
    except ImportError:
        mem = 6
    return max(1, min(cpu, mem, 8))
