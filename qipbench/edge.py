"""Quantum Hadamard Edge Detection (QHED, Yao et al., Phys. Rev. X 7, 031041, 2017).

The image is amplitude-encoded on n data qubits next to one ancilla (qubit 0):

    H_anc . D . H_anc |0>|img>,   D = cyclic decrement on all n+1 qubits

After the circuit, the amplitude of basis state |2i+1> (ancilla = 1) equals
(c_i - c_{i+1}) / 2, so measuring odd states yields every horizontal neighbour
difference in one shot of the whole register. Running the same circuit on the
transposed image gives vertical differences. Only N data amplitudes + 1 ancilla
are needed, versus N gradient evaluations classically.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import StatePreparation

from . import metrics
from .backend import execute


def increment(n: int) -> QuantumCircuit:
    """|x> -> |x + 1 mod 2^n> as a ladder of multi-controlled X gates."""
    qc = QuantumCircuit(n, name="+1")
    for k in range(n - 1, 0, -1):
        qc.mcx(list(range(k)), k)
    qc.x(0)
    return qc


def qhed_circuit(img: np.ndarray) -> tuple[QuantumCircuit, float]:
    vec = img.ravel().astype(float)
    norm = float(np.linalg.norm(vec))
    n = int(np.log2(vec.size))
    qc = QuantumCircuit(n + 1, name="QHED")
    if norm < 1e-12:
        return qc, 0.0
    qc.append(StatePreparation(vec / norm), list(range(1, n + 1)))
    qc.h(0)
    qc.compose(increment(n + 1).inverse(), inplace=True)
    qc.h(0)
    return qc, norm


def classical_differences(img: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """|I(r,c) - I(r,c+1)| and |I(r,c) - I(r+1,c)|; the last column/row has no neighbour."""
    h = np.zeros_like(img)
    v = np.zeros_like(img)
    h[:, :-1] = np.abs(img[:, :-1] - img[:, 1:])
    v[:-1, :] = np.abs(img[:-1, :] - img[1:, :])
    return h, v


def sobel_edges(img: np.ndarray) -> np.ndarray:
    gx = cv2.Sobel(img.astype(np.float32), cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(img.astype(np.float32), cv2.CV_32F, 0, 1, ksize=3)
    return np.hypot(gx, gy) / 4.0          # rescale so a unit step gives magnitude ~1


@dataclass
class EdgeResult:
    image: np.ndarray
    horizontal: np.ndarray
    vertical: np.ndarray
    magnitude: np.ndarray
    edges: np.ndarray
    classical_magnitude: np.ndarray
    classical_edges: np.ndarray
    sobel_edges: np.ndarray
    metrics: dict
    circuit: QuantumCircuit


def _scan(img: np.ndarray, shots, noise, opt_level, seed):
    qc, norm = qhed_circuit(img)
    res = execute(qc, shots, noise, opt_level, seed)
    p = res.distribution / max(res.distribution.sum(), 1e-300)
    diff = 2 * norm * np.sqrt(p[1::2])          # amplitude (c_i - c_{i+1}) / 2, times the norm
    diff = diff.reshape(img.shape)
    diff[:, -1] = 0.0                           # raster wrap-around (row end -> next row start)
    return diff, res, qc


def detect(img: np.ndarray, threshold: float = 0.2, shots: int | None = 8192,
           noise: float = 0.0, opt_level: int = 1, seed: int = 0) -> EdgeResult:
    h, rh, qc = _scan(img, shots, noise, opt_level, seed)
    vt, rv, _ = _scan(img.T, shots, noise, opt_level, seed + 1)
    v = vt.T
    mag = np.hypot(h, v)
    ch, cv = classical_differences(img)
    cmag = np.hypot(ch, cv)
    edges, cedges = mag > threshold, cmag > threshold
    sob = sobel_edges(img) > threshold
    scores = metrics.edge_scores(cedges, edges)
    m = {
        "qubits": rh.qubits, "depth": rh.depth, "cx": rh.cx, "gates": rh.gates,
        "circuits": 2, "shots_total": 2 * (shots or 0),
        "gradient_mae": float(np.mean(np.abs(mag - cmag))),
        "gradient_psnr": metrics.psnr(np.clip(cmag, 0, 1), np.clip(mag, 0, 1)),
        "fidelity": 0.5 * (metrics.classical_fidelity(rh.exact, rh.distribution)
                           + metrics.classical_fidelity(rv.exact, rv.distribution)),
        **{f"edge_{k}": val for k, val in scores.items()},
        "sobel_f1": metrics.edge_scores(sob, edges)["f1"],
        "simulate_s": rh.simulate_s + rv.simulate_s,
    }
    return EdgeResult(img, h, v, mag, edges, cmag, cedges, sob, m, qc)
