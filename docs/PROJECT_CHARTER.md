# Project Charter: QIP-Bench

**Course:** CSE3728 Quantum Image Processing and Emerging Visual Computing · BML Munjal University · 2026-27
**Problem statement:** 9. What really determines the performance of a quantum image-processing system?
**Team:** _<names, roll numbers>_  **Faculty:** Dr. Maheshwar Dwivedy, Dr. Kiran Khatter

## Problem
No single measure can judge a QIP system's performance. Practitioners compare encodings by qubit count alone
and ignore circuit structure, measurement budget, noise and reconstruction. The result is wrong design choices
and wasted hardware time.

## Objective
Build an empirical framework that measures which design factors most influence the **quality**,
**efficiency** and **reliability** of small-scale quantum image processing. Deliver it as a reproducible
toolkit and an interactive dashboard.

## Scope
* Representations: FRQI, NEQR and amplitude encoding (QPIE), each with a baseline and an optimized circuit structure.
* Operations: in-circuit intensity inversion (k stages) and Quantum Hadamard Edge Detection.
* Factors: image size, bit depth, interpolation, normalisation, circuit structure, transpiler level,
  operations, shots, noise, reconstruction estimator, missing-pixel fill, image content.
* Platform: Qiskit 2.x + Qiskit Aer simulator, with a uniform depolarising + readout noise model.
* Dataset: camera (natural), Shepp–Logan phantom (medical), coins, moon, gradient, checkerboard, disk, blocks.
  User uploads are supported.

**Out of scope:** execution on real IBM hardware, colour images, images larger than 32×32.

## Deliverables
| Phase | Deliverable | Location |
|---|---|---|
| A1 | Toy-image FRQI/NEQR encoding and decoding with numerical checks | `notebooks/01_encoding_fundamentals.ipynb` |
| A2 | Quantum edge-detection prototype with classical pre/post-processing | `notebooks/02_quantum_edge_detection.ipynb`, `qipbench/edge.py` |
| A3 | Full pipeline, controlled experiments, factor ranking, dashboard, report | `qipbench/`, `results/REPORT.md`, `web/` |

## Timeline
| Week (2026) | Milestone |
|---|---|
| 27 Jul – 16 Aug | Linear algebra and Qiskit basics; toy circuits (H, CNOT, Bell states) |
| 17 Aug – 13 Sep | Preprocessing module; FRQI and NEQR encoders; exact round-trip tests |
| **17 Sep (A1)** | Charter, encoding notebook, individual reflections |
| 20 Sep – 11 Oct | Optimized circuit structures; noise model; QHED edge detection |
| **Mid-term (A2)** | Working prototype, progress report, contribution matrix |
| 12 Oct – 8 Nov | OFAT and factorial studies; statistical analysis; dashboard |
| 9 Nov – 24 Nov | Final report, presentation, demo video |
| **End-term (A3)** | Repository, report, live demo, peer evaluation |

## Feasibility and resources
* Exact simulation up to about 18 qubits. Noisy trajectory simulation is practical up to about 12 qubits,
  which sets the 4×4 noisy baseline.
* The full study (≈ 4 500 pipeline runs) takes ≈ 10–20 min on an 8-core laptop. `--quick` takes ≈ 1 min.

## Roles (rotate each phase; everyone must be able to explain every module)
| Role | A1 | A2 | A3 |
|---|---|---|---|
| Encoding and circuits | _member 1_ | _member 2_ | _member 3_ |
| Preprocessing and metrics | _member 2_ | _member 3_ | _member 1_ |
| Experiments and analysis | _member 3_ | _member 1_ | _member 2_ |
| Dashboard and documentation | _member 4_ | _member 4_ | _member 4_ |

## Risks
| Risk | Mitigation |
|---|---|
| Noisy simulation too slow | Separate noisy baseline at 4×4; parallel worker pool capped by available memory |
| Statistical noise hides effects | 3 images × 3 seeds per OFAT level; replicated factorial with p-values |
| Over-claiming hardware relevance | Explicit threats-to-validity section; CNOT counts stated as lower bounds |
