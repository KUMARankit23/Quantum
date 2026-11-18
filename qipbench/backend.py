"""Circuit execution: transpilation, noise models and Aer simulation.

Two execution modes:
    shots=None  exact Born-rule probabilities from the statevector (the infinite-shot limit)
    shots=k     k measurement samples on AerSimulator, optionally with a noise model

The noise model is a single-knob depolarising model so that "noise level" is one factor:
    1-qubit gates : depolarising, p / 10
    CNOT          : depolarising, p
    readout       : symmetric bit-flip, p
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from functools import lru_cache

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError, depolarizing_error

BASIS_GATES = ["rz", "sx", "x", "cx"]
AER_THREADS = int(os.environ.get("QIPBENCH_AER_THREADS", "0"))   # 0 = Aer decides; 1 inside worker pools


@dataclass
class ExecutionResult:
    distribution: np.ndarray   # counts (shots) or probabilities (exact), indexed by basis state
    exact: np.ndarray          # ideal noiseless probabilities of the same circuit
    shots: int | None
    noise: float
    qubits: int
    logical_depth: int
    depth: int                 # depth after transpilation to BASIS_GATES
    cx: int
    gates: int                 # total gate count after transpilation (excl. barrier/measure)
    transpile_s: float
    simulate_s: float


@lru_cache(maxsize=32)
def noise_model(p: float) -> NoiseModel | None:
    if p <= 0:
        return None
    nm = NoiseModel(basis_gates=BASIS_GATES)
    nm.add_all_qubit_quantum_error(depolarizing_error(p / 10, 1), ["sx", "x"])
    nm.add_all_qubit_quantum_error(depolarizing_error(p, 2), ["cx"])
    nm.add_all_qubit_readout_error(ReadoutError([[1 - p, p], [p, 1 - p]]))
    return nm


def circuit_cost(qc: QuantumCircuit, opt_level: int = 1, seed: int = 0) -> tuple[QuantumCircuit, float]:
    t0 = time.perf_counter()
    tqc = transpile(qc, basis_gates=BASIS_GATES, optimization_level=opt_level, seed_transpiler=seed)
    return tqc, time.perf_counter() - t0


def exact_probabilities(qc: QuantumCircuit) -> np.ndarray:
    """Born-rule probabilities of every basis state (Aer statevector, no sampling)."""
    c = qc.remove_final_measurements(inplace=False)
    c.save_probabilities()
    return np.asarray(AerSimulator(method="statevector", max_parallel_threads=AER_THREADS).run(c).result().data()["probabilities"])


def _counts_to_vector(counts: dict[str, int], n_qubits: int) -> np.ndarray:
    vec = np.zeros(2 ** n_qubits)
    for key, c in counts.items():
        vec[int(key.replace(" ", ""), 2)] += c
    return vec


def execute(qc: QuantumCircuit, shots: int | None = 4096, noise: float = 0.0,
            opt_level: int = 1, seed: int = 0) -> ExecutionResult:
    """Run a measurement-free state-preparation circuit and return its outcome distribution."""
    tqc, t_transpile = circuit_cost(qc, opt_level, seed)
    ops = tqc.count_ops()
    gates = sum(v for k, v in ops.items() if k not in ("barrier", "measure"))

    t0 = time.perf_counter()
    exact = exact_probabilities(tqc)
    if shots is None:
        if noise > 0:
            raise ValueError("exact mode is noiseless; set shots to simulate noise")
        dist = exact.copy()
    else:
        meas = tqc.copy()
        meas.measure_all()
        sim = AerSimulator(noise_model=noise_model(round(noise, 12)), seed_simulator=seed,
                           max_parallel_threads=AER_THREADS)
        counts = sim.run(meas, shots=shots).result().get_counts()
        dist = _counts_to_vector(counts, qc.num_qubits)
    t_sim = time.perf_counter() - t0

    return ExecutionResult(
        distribution=dist, exact=exact, shots=shots, noise=noise, qubits=qc.num_qubits,
        logical_depth=qc.depth(), depth=tqc.depth(), cx=int(ops.get("cx", 0)), gates=int(gates),
        transpile_s=t_transpile, simulate_s=t_sim,
    )
