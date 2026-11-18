# Research Methodology

**Problem 9: What really determines the performance of a quantum image-processing system?**

No single measure can judge a quantum image-processing (QIP) system. Image size, intensity representation,
preprocessing, circuit structure, number of operations, measurement and reconstruction all shape the result.
QIP-Bench treats each of these as an **experimental factor**. It varies them under control and measures their
influence on three separate performance dimensions.

---

## 1. System under test

```
source image ─► preprocess ─► encode ─► operate ─► measure ─► reconstruct ─► evaluate
 (photo,         resize        FRQI      k inversion  shots      estimator      quality
  phantom,       normalise     NEQR      stages,      noise p    missing-pixel  efficiency
  synthetic,     quantise      QPIE      QHED                    fill           reliability
  upload)        (bit depth)
```

| Stage | Module | Key equations / decisions |
|---|---|---|
| Preprocess | `qipbench/images.py` | power-of-two resize (nearest / bilinear / bicubic / area), min-max or histogram-equalisation, uniform quantisation to 2^b levels |
| FRQI | `qipbench/encoders.py` | θᵢ = (π/2)·Iᵢ; uniformly controlled R_Y(2θᵢ); decode θ = arcsin √P(1 \| i) |
| NEQR | `qipbench/encoders.py` | grey level Cᵢ ∈ {0,1}^q as a basis state via multi-controlled X; decode by majority vote |
| QPIE | `qipbench/encoders.py` | cᵢ = Iᵢ/‖I‖ via `StatePreparation`; decode ‖I‖·√pᵢ |
| Operation | `qipbench/pipeline.py` | inversion I → 1 − I (FRQI: X on colour qubit; NEQR: X on all colour qubits), barrier-separated stages |
| QHED | `qipbench/edge.py` | H_anc · D · H_anc; amplitude of \|2i+1⟩ = (cᵢ − cᵢ₊₁)/2 |
| Execute | `qipbench/backend.py` | transpile to {rz, sx, x, cx}; Aer statevector (exact) or shot sampling with noise |
| Evaluate | `qipbench/metrics.py` | PSNR, SSIM, exact-level accuracy, Bhattacharyya fidelity, TVD, coverage, edge F1/IoU |

### Circuit-structure variants (same state, different engineering)

| Encoding | `baseline` | `optimized` |
|---|---|---|
| FRQI | one n-controlled R_Y per pixel inside X-sandwiches | Gray-code uniformly controlled R_Y (Möttönen 2004): exactly 2ⁿ R_Y + 2ⁿ CNOT. Verified operator-equal to Qiskit `UCRYGate` in the tests |
| NEQR | one n-controlled X per (pixel, set bit) | Gray-code pixel order shares X-flips between neighbours; one ancilla holds the pixel condition, so each pixel costs 2 MCX + fan-out CNOTs |

## 2. Hypotheses

| # | Hypothesis | Tested by |
|---|---|---|
| H1 | Circuit structure (decomposition) matters more for cost and noisy quality than qubit count | `structure`, `opt_level`, factorial |
| H2 | FRQI quality is limited by measurement statistics, NEQR quality by pixel coverage | `shots`, `fill`, `image_size` |
| H3 | NEQR (basis encoding) is more noise-robust than FRQI (angle encoding) up to a threshold | `noise`, factorial noise × structure |
| H4 | Bit depth costs qubits only in NEQR | `bit_depth` |
| H5 | Resolution dominates end-to-end fidelity to the source; the quantum channel dominates fidelity to the loaded image | `image_size`, `interpolation`, `normalization` |
| H6 | Pixel-wise operations add little error compared with state preparation | `operations` |
| H7 | The classical reconstruction estimator changes quality at zero quantum cost | `estimator` |
| H8 | QHED is exact in the infinite-shot limit but weak edges need many shots | edge study |

## 3. Experimental design

### 3.1 One-factor-at-a-time (OFAT) sweeps: *shape* of each response

Each factor is swept over a wide range around a baseline. Each level runs on 3 images (camera, Shepp–Logan
phantom, synthetic blocks) × 3 simulator seeds.

| Baseline | Size | Bit depth | Shots | Noise | Structure | Transpiler |
|---|---|---|---|---|---|---|
| Noiseless | 8×8 | 8 | 4096 | 0 | optimized | 1 |
| Noisy | 4×4 | 4 | 4096 | 1e-3 | optimized | 1 |

There are two baselines because noisy trajectory simulation costs about 2^qubits × gates × shots. A 15-qubit
NEQR 8×8 circuit with more than 5 000 CNOTs takes over a minute per noisy run. Reporting that limit is
itself part of the efficiency answer.

### 3.2 Full 2⁷ factorial screening: *ranking* and *interactions*

| Factor | Low (−1) | High (+1) |
|---|---|---|
| Image size | 4 (NEQR: 2) | 8 (NEQR: 4) |
| Bit depth | 2 | 8 (NEQR: 4) |
| Shots | 256 | 8192 |
| Noise p | 0 | 2e-3 |
| Circuit structure | baseline | optimized |
| Transpiler level | 0 | 3 |
| Operations | 0 | 4 |

128 cells × 3 images × 2 seeds = 768 runs per encoding. All main effects and all 21 two-factor
interactions are estimated with an orthogonal ±1 regression. Each term's **% contribution** is
SS_term / SS_total. Significance uses a t-test on the residual error.

### 3.3 Edge-detection study (QHED)

Shots (256 → 65 536, exact), size (4 → 32), noise (0 → 3e-3) and threshold (0.05 → 0.4), on blocks,
phantom and camera images. Quality is the edge-map F1 against the exact classical forward differences,
with the F1 against Sobel given as context.

## 4. Performance dimensions and metrics

| Dimension | Primary metric | Supporting metrics |
|---|---|---|
| **Quality** | PSNR (dB) of the reconstruction vs the classically expected image | SSIM, exact-level accuracy, end-to-end PSNR vs the source (64×64), edge F1 |
| **Efficiency** | CNOT count after transpiling to {rz, sx, x, cx} | qubits, depth, wall-clock time, shots × depth |
| **Reliability** | Std of PSNR across simulator seeds | success rate P(SSIM ≥ 0.90), distribution fidelity, coverage |

**Influence measures**

* OFAT: η² = SS_between-levels / SS_total, the share of variance a factor explains along its own sweep.
* Factorial: % contribution of main effects and interactions, with p-values.

PSNR is capped at 60 dB for perfect reconstructions so that means and effects stay finite.

## 5. Reproducibility

* Seeds: the transpiler and simulator are seeded per run (`seed` = 0, 1, 2), so every number in
  `results/` regenerates bit-for-bit on the same library versions.
* `python -m qipbench run` regenerates all CSVs, figures, `summary.json` and `REPORT.md`. Use
  `--quick` for a 1-minute smoke test.
* `pytest` checks every quantum routine against an exact classical answer: round trips, state definitions,
  operator equivalence with Qiskit's `UCRYGate`, decrement unitary, QHED = classical differences.

## 6. Threats to validity

* The noise model is uniform depolarising + readout. Real devices add crosstalk, leakage and coupling-map
  SWAPs, which would penalise deep NEQR circuits further.
* No coupling map is used, so CNOT counts are lower bounds for hardware.
* Noisy experiments use small images (4×4, ≤ 4-bit NEQR). Conclusions are about small-scale systems, which is
  the scope of the problem statement.
* Three test images span natural, medical and synthetic content. The `image` study extends this to eight
  images to check how much content matters.

## References

1. P. Q. Le, F. Dong, K. Hirota, "A flexible representation of quantum images", *Quantum Inf. Process.* 10, 63 (2011).
2. Y. Zhang, K. Lu, Y. Gao, M. Wang, "NEQR: a novel enhanced quantum representation of digital images", *Quantum Inf. Process.* 12, 2833 (2013).
3. X.-W. Yao et al., "Quantum image processing and its application to edge detection", *Phys. Rev. X* 7, 031041 (2017).
4. M. Möttönen, J. Vartiainen, V. Bergholm, M. Salomaa, "Quantum circuits for general multiqubit gates", *PRL* 93, 130502 (2004).
5. M. Nielsen, I. Chuang, *Quantum Computation and Quantum Information*, CUP (2010).
6. R. C. Gonzalez, R. E. Woods, *Digital Image Processing*, 4th ed., Pearson (2018).
