"""Correctness tests: every quantum routine is checked against an exact classical answer."""

import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.circuit.library import UCRYGate
from qiskit.quantum_info import Operator, Statevector

from qipbench import edge, images, metrics
from qipbench.backend import execute
from qipbench.encoders import FRQI, NEQR, Amplitude, gray
from qipbench.pipeline import PipelineConfig, run

RNG = np.random.default_rng(7)


def random_image(size, bits=8):
    return np.rint(RNG.random((size, size)) * (2 ** bits - 1)) / (2 ** bits - 1)


# ------------------------------------------------------------------ encodings

@pytest.mark.parametrize("enc", [FRQI(), NEQR(), Amplitude()])
@pytest.mark.parametrize("structure", ["baseline", "optimized"])
@pytest.mark.parametrize("size", [2, 4])
def test_exact_roundtrip(enc, structure, size):
    """Encode -> exact probabilities -> decode must return the image."""
    img = random_image(size)
    e = enc.encode(img, 8, structure)
    res = execute(e.circuit, shots=None)
    rec, coverage = enc.decode(res.distribution, img.shape, e)
    assert np.allclose(rec, img, atol=1e-9)
    assert res.qubits == enc.n_qubits(img.shape, 8, structure)


def test_frqi_state_matches_definition():
    img = random_image(2)
    e = FRQI().encode(img, structure="optimized")
    theta = (np.pi / 2) * img.ravel()
    expected = np.concatenate([np.cos(theta), np.sin(theta)]) / 2      # index = colour * 4 + position
    assert np.allclose(Statevector(e.circuit).data.real, expected, atol=1e-9)


def test_gray_code_multiplexor_equals_qiskit_ucry():
    angles = RNG.random(8) * np.pi
    ours = QuantumCircuit(4)
    FRQI._multiplexed_gray(ours, angles, [0, 1, 2], 3)
    ref = QuantumCircuit(4)
    ref.append(UCRYGate(list(angles)), [3, 0, 1, 2])
    assert Operator(ours).equiv(Operator(ref))


def test_structures_prepare_identical_states():
    img = random_image(4)
    for enc in (FRQI(), NEQR()):
        a = Statevector(enc.encode(img, 8, "baseline").circuit).probabilities()
        b = Statevector(enc.encode(img, 8, "optimized").circuit).probabilities()
        b = b.reshape(-1, a.size).sum(axis=0)          # optimized NEQR has an ancilla in |0>
        assert np.allclose(a, b, atol=1e-9)


def test_optimized_frqi_uses_exactly_n_pixels_cnots():
    for size in (2, 4, 8):
        res = execute(FRQI().encode(random_image(size), structure="optimized").circuit, shots=None, opt_level=0)
        assert res.cx == size * size


def test_neqr_inversion_is_complement():
    img = random_image(4, bits=4)
    enc = NEQR()
    e = enc.encode(img, 4)
    enc.invert(e.circuit, e)
    rec, _ = enc.decode(execute(e.circuit, shots=None).distribution, img.shape, e)
    assert np.allclose(rec, 1 - img)


def test_gray_code_adjacent_differ_by_one_bit():
    assert all(bin(gray(i) ^ gray(i + 1)).count("1") == 1 for i in range(255))


# ------------------------------------------------------------------ measurement & reconstruction

def test_unsampled_pixels_are_filled():
    cfg = PipelineConfig(encoding="neqr", size=8, bit_depth=4, shots=16, fill="neighbor")
    r = run(cfg)
    assert r.metrics["coverage"] < 1
    assert np.isfinite(r.reconstructed).all()


def test_more_shots_improve_frqi():
    low = np.mean([run(PipelineConfig(shots=128, seed=s)).metrics["psnr"] for s in range(3)])
    high = np.mean([run(PipelineConfig(shots=16384, seed=s)).metrics["psnr"] for s in range(3)])
    assert high > low + 5


def test_noise_reduces_distribution_fidelity():
    clean = run(PipelineConfig(size=4, noise=0.0)).metrics["fidelity"]
    noisy = run(PipelineConfig(size=4, noise=1e-2, structure="baseline")).metrics["fidelity"]
    assert noisy < clean


def test_operations_parity():
    even = run(PipelineConfig(size=4, shots=None, operations=2))
    odd = run(PipelineConfig(size=4, shots=None, operations=3))
    assert np.allclose(even.reconstructed, even.preprocessed.quantized, atol=1e-9)
    assert np.allclose(odd.reconstructed, 1 - odd.preprocessed.quantized, atol=1e-9)


# ------------------------------------------------------------------ edge detection

def test_decrement_circuit():
    dec = edge.increment(3).inverse()
    for x in range(8):
        sv = Statevector.from_int(x, 8).evolve(dec)
        assert np.argmax(sv.probabilities()) == (x - 1) % 8


def test_qhed_exact_equals_classical_differences():
    img = images.preprocess(images.load_standard("phantom"), 8).quantized
    r = edge.detect(img, shots=None)
    assert np.allclose(r.magnitude, r.classical_magnitude, atol=1e-9)
    assert r.metrics["edge_f1"] == 1.0


# ------------------------------------------------------------------ preprocessing & metrics

def test_quantize_levels():
    q, lv = images.quantize(np.linspace(0, 1, 11), 2)
    assert set(lv) <= {0, 1, 2, 3} and q.min() == 0 and q.max() == 1


def test_preprocess_rejects_non_power_of_two():
    with pytest.raises(ValueError):
        images.preprocess(images.load_standard("camera"), 6)


def test_metrics_basics():
    a = random_image(8)
    assert metrics.psnr(a, a) == metrics.PSNR_CAP
    assert metrics.ssim(a, a) == pytest.approx(1.0)
    assert metrics.ssim(a[:2, :2], a[:2, :2]) == pytest.approx(1.0)
    assert metrics.classical_fidelity(np.array([.5, .5]), np.array([.5, .5])) == pytest.approx(1.0)
    s = metrics.edge_scores(np.eye(4, dtype=bool), np.eye(4, dtype=bool))
    assert s["f1"] == 1.0 and s["iou"] == 1.0
