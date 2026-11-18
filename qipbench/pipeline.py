"""End-to-end quantum image-processing pipeline.

    classical preprocessing -> quantum encoding -> quantum operations -> measurement
    -> decoding / reconstruction -> classical post-processing -> evaluation

Every argument of :class:`PipelineConfig` is a controllable design factor of the study.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, replace

import numpy as np

from . import images, metrics
from .backend import execute
from .encoders import get_encoder

QUALITY_THRESHOLD_SSIM = 0.90      # a run "succeeds" when its reconstruction reaches this SSIM


@dataclass(frozen=True)
class PipelineConfig:
    encoding: str = "frqi"              # frqi | neqr | amplitude
    image: str = "camera"               # standard image name (see images.STANDARD_IMAGES)
    size: int = 8                       # image side, power of two
    bit_depth: int = 8                  # grey-level quantisation (NEQR: colour qubits)
    interpolation: str = "area"         # nearest | bilinear | bicubic | area
    normalization: str = "minmax"       # none | minmax | equalize
    structure: str = "optimized"        # baseline | optimized circuit decomposition
    opt_level: int = 1                  # Qiskit transpiler optimisation level 0..3
    operations: int = 0                 # number of in-circuit inversion stages
    shots: int | None = 4096            # None = exact (infinite-shot) probabilities
    noise: float = 0.0                  # depolarising + readout error rate p
    estimator: str = "auto"             # frqi: conditional|marginal, neqr: majority|mean
    fill: str = "neighbor"              # unsampled pixels: neighbor | zero
    seed: int = 0

    def with_(self, **kw) -> "PipelineConfig":
        return replace(self, **kw)


@dataclass
class PipelineResult:
    config: PipelineConfig
    source: np.ndarray
    preprocessed: images.Preprocessed
    expected: np.ndarray            # classical result of the same operations (ground truth)
    reconstructed: np.ndarray
    metrics: dict
    circuit: object                 # the logical (pre-transpilation) circuit
    distribution: np.ndarray | None = None   # measured counts (or exact probabilities) per basis state
    layout: dict | None = None               # register sizes needed to interpret the distribution

    def row(self) -> dict:
        cfg = asdict(self.config)
        cfg["shots"] = cfg["shots"] if cfg["shots"] is not None else 0
        return {**cfg, **self.metrics}


def run(config: PipelineConfig, source: np.ndarray | None = None) -> PipelineResult:
    t_start = time.perf_counter()
    enc = get_encoder(config.encoding)
    estimator = enc.estimators[0] if config.estimator == "auto" else config.estimator
    if source is None:
        source = images.load_standard(config.image)

    pre = images.preprocess(source, config.size, config.interpolation,
                            config.normalization, config.bit_depth)
    encoded = enc.encode(pre.quantized, config.bit_depth, config.structure)
    qc = encoded.circuit
    for _ in range(config.operations):
        qc.barrier()                                # each stage is a separate processing step
        enc.invert(qc, encoded)
    expected = 1.0 - pre.quantized if config.operations % 2 else pre.quantized

    res = execute(qc, config.shots, config.noise, config.opt_level, config.seed)
    recon, coverage = enc.decode(res.distribution, pre.quantized.shape, encoded, estimator, config.fill)

    # end-to-end comparison happens in the original intensity domain, so undo the inversion
    restored = 1.0 - recon if config.operations % 2 else recon
    e2e = images.upsample(restored, images.REFERENCE_RES)

    m = {
        "qubits": res.qubits,
        "logical_depth": res.logical_depth,
        "depth": res.depth,
        "cx": res.cx,
        "gates": res.gates,
        "mse": metrics.mse(expected, recon),
        "psnr": metrics.psnr(expected, recon),
        "ssim": metrics.ssim(expected, recon),
        "level_accuracy": metrics.level_accuracy(expected, recon, config.bit_depth),
        "fidelity": metrics.classical_fidelity(res.exact, res.distribution),
        "tvd": metrics.tvd(res.exact, res.distribution),
        "coverage": coverage,
        "e2e_psnr": metrics.psnr(pre.reference, e2e),
        "e2e_ssim": metrics.ssim(pre.reference, e2e),
        "preprocess_psnr": metrics.psnr(pre.reference, images.upsample(pre.quantized)),
        "entropy": metrics.image_entropy(pre.quantized),
        "transpile_s": res.transpile_s,
        "simulate_s": res.simulate_s,
        "total_s": time.perf_counter() - t_start,
        "shot_cost": (config.shots or 0) * res.depth,
    }
    m["success"] = float(m["ssim"] >= QUALITY_THRESHOLD_SSIM)
    layout = {"position": encoded.n_position, "color": len(encoded.color_qubits),
              "ancilla": len(encoded.ancilla_qubits), "norm": encoded.side_info.get("norm")}
    return PipelineResult(config, source, pre, expected, recon, m, qc, res.distribution, layout)
