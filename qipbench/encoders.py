"""Quantum image representations: FRQI, NEQR and amplitude encoding (QPIE).

Qubit layout (Qiskit is little-endian, qubit 0 is the least significant bit):

    q[0 .. n-1]        position register, pixel index i = row * W + col
    q[n .. n+c-1]      colour register (FRQI: 1 qubit, NEQR: bit_depth qubits)
    q[n+c ..]          ancillas (NEQR 'optimized' structure only)

A measured basis-state index therefore decomposes as
    index = ancilla * 2^(n+c) + colour * 2^n + position
which lets the decoders reshape a probability vector instead of parsing bitstrings.

Two circuit structures are offered for each method so that *circuit structure* can be
studied as a factor while the encoded state stays identical:

    FRQI  baseline : one multi-controlled RY per pixel (X-sandwiches select the pixel)
          optimized: Gray-code uniformly controlled RY, exactly 2^n RY + 2^n CNOT
    NEQR  baseline : one multi-controlled X per (pixel, set bit) with per-pixel X-sandwiches
          optimized: Gray-code pixel order (X flips shared between neighbours) and one
                     ancilla that holds the pixel condition so each pixel costs 2 MCX
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import RYGate, StatePreparation

STRUCTURES = ("baseline", "optimized")


@dataclass
class EncodedImage:
    circuit: QuantumCircuit
    position_qubits: list[int]
    color_qubits: list[int]
    ancilla_qubits: list[int] = field(default_factory=list)
    side_info: dict = field(default_factory=dict)     # classical data needed for decoding

    @property
    def n_position(self) -> int:
        return len(self.position_qubits)


def gray(i: int) -> int:
    return i ^ (i >> 1)


def _n_position_qubits(shape: tuple[int, int]) -> int:
    n_pix = shape[0] * shape[1]
    n = int(np.log2(n_pix))
    if 2 ** n != n_pix:
        raise ValueError("number of pixels must be a power of two")
    return n


def _fill_unsampled(img: np.ndarray, valid: np.ndarray, method: str) -> np.ndarray:
    """Positions never observed in the measurement record have no estimate."""
    out = img.copy()
    if valid.all():
        return out
    if method == "zero" or not valid.any():
        out[~valid] = 0.0
        return out
    if method != "neighbor":
        raise ValueError("fill must be 'zero' or 'neighbor'")
    known = valid.copy()
    for _ in range(max(img.shape)):                     # grow estimates from known neighbours
        if known.all():
            break
        padded = np.pad(np.where(known, out, 0.0), 1)
        weight = np.pad(known.astype(float), 1)
        s = padded[:-2, 1:-1] + padded[2:, 1:-1] + padded[1:-1, :-2] + padded[1:-1, 2:]
        w = weight[:-2, 1:-1] + weight[2:, 1:-1] + weight[1:-1, :-2] + weight[1:-1, 2:]
        grow = (~known) & (w > 0)
        out[grow] = s[grow] / w[grow]
        known = known | grow
    return out


# =========================================================================== FRQI

class FRQI:
    """Flexible Representation of Quantum Images (Le, Dong & Hirota, 2011).

    |I> = 1/sqrt(N) * sum_i (cos(theta_i)|0> + sin(theta_i)|1>) (x) |i>,  theta_i = (pi/2) * I_i
    """

    name = "frqi"
    estimators = ("conditional", "marginal")

    @staticmethod
    def angles(img: np.ndarray) -> np.ndarray:
        return (np.pi / 2) * np.clip(img.ravel(), 0, 1)

    def n_qubits(self, shape: tuple[int, int], bit_depth: int = 8, structure: str = "optimized") -> int:
        return _n_position_qubits(shape) + 1

    def encode(self, img: np.ndarray, bit_depth: int = 8, structure: str = "optimized") -> EncodedImage:
        n = _n_position_qubits(img.shape)
        pos, color = list(range(n)), n
        qc = QuantumCircuit(n + 1, name="FRQI")
        qc.h(pos)
        ry_angles = 2 * self.angles(img)                 # RY(2θ) maps |0> -> cos θ|0> + sin θ|1>
        if structure == "baseline":
            self._multiplexed_naive(qc, ry_angles, pos, color)
        elif structure == "optimized":
            self._multiplexed_gray(qc, ry_angles, pos, color)
        else:
            raise ValueError(f"structure must be one of {STRUCTURES}")
        return EncodedImage(qc, pos, [color])

    @staticmethod
    def _multiplexed_naive(qc: QuantumCircuit, ry_angles: np.ndarray, ctrl: list[int], target: int) -> None:
        n = len(ctrl)
        for i, a in enumerate(ry_angles):
            if abs(a) < 1e-12:
                continue
            zeros = [ctrl[k] for k in range(n) if not (i >> k) & 1]
            if zeros:
                qc.x(zeros)
            qc.append(RYGate(a).control(n, annotated=False), ctrl + [target])
            if zeros:
                qc.x(zeros)

    @staticmethod
    def _multiplexed_gray(qc: QuantumCircuit, ry_angles: np.ndarray, ctrl: list[int], target: int) -> None:
        """Uniformly controlled RY (Möttönen et al., 2004).

        Sequence RY(β_0) CX(c_0) RY(β_1) CX(c_1) ... where c_j is the bit that flips between
        gray(j) and gray(j+1). For control value x the target sees the net angle
            α_x = Σ_j (-1)^popcount(x & gray(j)) β_j   =>   β = Mᵀ α / 2^n.
        """
        n = len(ctrl)
        size = 2 ** n
        m = np.array([[(-1) ** bin(x & gray(j)).count("1") for j in range(size)] for x in range(size)])
        beta = m.T @ ry_angles / size
        for j in range(size):
            if abs(beta[j]) > 1e-12:
                qc.ry(float(beta[j]), target)
            flip = gray(j) ^ gray((j + 1) % size)
            qc.cx(ctrl[flip.bit_length() - 1], target)

    def decode(self, dist: np.ndarray, shape: tuple[int, int], enc: EncodedImage,
               estimator: str = "conditional", fill: str = "neighbor") -> tuple[np.ndarray, float]:
        """Return (image in [0,1], coverage) from a probability or count vector over all qubits."""
        n_pix = shape[0] * shape[1]
        table = dist.reshape(-1, 2, n_pix).sum(axis=0)    # rows: colour 0/1, cols: position
        n0, n1 = table
        seen = (n0 + n1) > 0
        if estimator == "conditional":                   # P(colour=1 | position) = sin²θ
            p1 = np.divide(n1, n0 + n1, out=np.zeros(n_pix), where=seen)
        elif estimator == "marginal":                    # P(colour=1, position) = sin²θ / N
            p1 = np.clip(n_pix * n1 / max(table.sum(), 1e-300), 0, 1)
            seen = np.ones(n_pix, bool)
        else:
            raise ValueError(f"FRQI estimator must be one of {self.estimators}")
        img = (2 / np.pi) * np.arcsin(np.sqrt(np.clip(p1, 0, 1)))
        img = _fill_unsampled(img.reshape(shape), seen.reshape(shape), fill)
        return np.clip(img, 0, 1), float(seen.mean())

    def invert(self, qc: QuantumCircuit, enc: EncodedImage) -> None:
        """θ -> π/2 - θ (I -> 1 - I) is a single X on the colour qubit."""
        qc.x(enc.color_qubits)


# =========================================================================== NEQR

class NEQR:
    """Novel Enhanced Quantum Representation (Zhang et al., 2013).

    |I> = 1/sqrt(N) * sum_i |C_i> (x) |i>,  C_i the q-bit binary grey level of pixel i
    """

    name = "neqr"
    estimators = ("majority", "mean")

    def n_qubits(self, shape: tuple[int, int], bit_depth: int = 8, structure: str = "optimized") -> int:
        return _n_position_qubits(shape) + bit_depth + (1 if structure == "optimized" else 0)

    def encode(self, img: np.ndarray, bit_depth: int = 8, structure: str = "optimized") -> EncodedImage:
        n = _n_position_qubits(img.shape)
        top = 2 ** bit_depth - 1
        values = np.rint(np.clip(img.ravel(), 0, 1) * top).astype(int)
        pos = list(range(n))
        color = list(range(n, n + bit_depth))
        if structure == "baseline":
            qc = QuantumCircuit(n + bit_depth, name="NEQR")
            qc.h(pos)
            for i, v in enumerate(values):
                if v == 0:
                    continue
                zeros = [pos[k] for k in range(n) if not (i >> k) & 1]
                if zeros:
                    qc.x(zeros)
                for b in range(bit_depth):
                    if (v >> b) & 1:
                        qc.mcx(pos, color[b])
                if zeros:
                    qc.x(zeros)
            return EncodedImage(qc, pos, color)
        if structure != "optimized":
            raise ValueError(f"structure must be one of {STRUCTURES}")

        anc = n + bit_depth
        qc = QuantumCircuit(n + bit_depth + 1, name="NEQR")
        qc.h(pos)
        flipped = 0                                     # bitmask of position qubits currently X-ed
        for j in range(2 ** n):
            i = gray(j)                                 # consecutive pixels differ in one bit
            v = values[i]
            if v == 0:
                continue
            want = ~i & (2 ** n - 1)                    # qubits that must be flipped to select i
            toggle = flipped ^ want
            if toggle:
                qc.x([pos[k] for k in range(n) if (toggle >> k) & 1])
            flipped = want
            bits = [color[b] for b in range(bit_depth) if (v >> b) & 1]
            if len(bits) == 1:
                qc.mcx(pos, bits[0])
            else:                                       # compute condition once, fan out, uncompute
                qc.mcx(pos, anc)
                for t in bits:
                    qc.cx(anc, t)
                qc.mcx(pos, anc)
        if flipped:
            qc.x([pos[k] for k in range(n) if (flipped >> k) & 1])
        return EncodedImage(qc, pos, color, [anc])

    def decode(self, dist: np.ndarray, shape: tuple[int, int], enc: EncodedImage,
               estimator: str = "majority", fill: str = "neighbor") -> tuple[np.ndarray, float]:
        n_pix = shape[0] * shape[1]
        q = len(enc.color_qubits)
        table = dist.reshape(-1, 2 ** q, n_pix).sum(axis=0)   # rows: grey level, cols: position
        seen = table.sum(axis=0) > 0
        if estimator == "majority":                         # basis encoding -> most frequent value
            values = table.argmax(axis=0).astype(float)
        elif estimator == "mean":
            levels = np.arange(2 ** q)[:, None]
            values = np.divide((levels * table).sum(axis=0), table.sum(axis=0),
                               out=np.zeros(n_pix), where=seen)
        else:
            raise ValueError(f"NEQR estimator must be one of {self.estimators}")
        img = values / (2 ** q - 1)
        img = _fill_unsampled(img.reshape(shape), seen.reshape(shape), fill)
        return np.clip(img, 0, 1), float(seen.mean())

    def invert(self, qc: QuantumCircuit, enc: EncodedImage) -> None:
        """C -> (2^q - 1) - C is X on every colour qubit."""
        qc.x(enc.color_qubits)


# =========================================================================== Amplitude (QPIE)

class Amplitude:
    """Quantum Probability Image Encoding: |I> = sum_i c_i |i>,  c_i = I_i / ||I||_2.

    Most qubit-efficient (log2 N), but the global norm ||I|| is classical side information
    and state preparation needs O(N) CNOTs.
    """

    name = "amplitude"
    estimators = ("sqrt",)

    def n_qubits(self, shape: tuple[int, int], bit_depth: int = 8, structure: str = "optimized") -> int:
        return _n_position_qubits(shape)

    def encode(self, img: np.ndarray, bit_depth: int = 8, structure: str = "optimized") -> EncodedImage:
        n = _n_position_qubits(img.shape)
        vec = np.clip(img.ravel(), 0, 1).astype(float)
        norm = float(np.linalg.norm(vec))
        if norm < 1e-12:
            vec, norm = np.eye(1, vec.size).ravel(), 0.0
        qc = QuantumCircuit(n, name="QPIE")
        qc.append(StatePreparation(vec / np.linalg.norm(vec)), list(range(n)))
        return EncodedImage(qc, list(range(n)), [], side_info={"norm": norm})

    def decode(self, dist: np.ndarray, shape: tuple[int, int], enc: EncodedImage,
               estimator: str = "sqrt", fill: str = "neighbor") -> tuple[np.ndarray, float]:
        p = dist / max(dist.sum(), 1e-300)
        img = enc.side_info["norm"] * np.sqrt(p)
        return np.clip(img.reshape(shape), 0, 1), float((dist > 0).mean())

    def invert(self, qc: QuantumCircuit, enc: EncodedImage) -> None:
        raise NotImplementedError("intensity inversion is not a unitary on amplitude-encoded images")


ENCODERS = {"frqi": FRQI(), "neqr": NEQR(), "amplitude": Amplitude()}


def get_encoder(name: str):
    try:
        return ENCODERS[name.lower()]
    except KeyError:
        raise ValueError(f"encoding must be one of {list(ENCODERS)}") from None
