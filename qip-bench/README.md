# QIP-Bench

### What really determines the performance of a quantum image-processing system?

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/<your-user>/qip-bench/blob/main/QIP_Bench_Colab.ipynb)
<!-- replace <your-user>/qip-bench with your GitHub repository after pushing -->

QIP-Bench is an **empirical performance-factor framework** for small-scale quantum image processing (QIP).
It runs complete pipelines on Qiskit Aer:

> classical preprocessing → quantum encoding (FRQI / NEQR / QPIE) → quantum operations (inversion, QHED edge detection)
> → measurement → reconstruction → classical post-processing

It then varies every design factor under control and ranks its influence on **quality**, **efficiency** and
**reliability**. Results come with a statistical report, three course notebooks and an interactive web dashboard.

*CSE3728 Quantum Image Processing & Emerging Visual Computing, BML Munjal University, 2026-27, Problem Statement 9.*

---

## Why it matters

Teams evaluating quantum imaging usually compare encodings by **qubit count**. Our measurements show that is
the wrong lens.

| Decision | What the data says | Impact |
|---|---|---|
| *Which circuit for the same encoding?* | The Gray-code FRQI needs **16 CNOTs vs 312** for the naive circuit on a 4×4 image. Under p = 10⁻³ noise PSNR rises from **17.4 dB to 27.8 dB** and the success rate from **0 % to 100 %**. | Circuit engineering is the cheapest win |
| *How many measurements to buy?* | FRQI quality is shot-limited (11 dB at 64 shots → 36 dB at 16 384). NEQR is exact once every pixel has been seen once. | Measurement budget is a first-class cost |
| *FRQI or NEQR?* | NEQR is perfect up to p = 3·10⁻³ and **collapses** at 10⁻² (9.6 dB). FRQI **degrades gracefully** (34 → 18 dB). NEQR costs ≈ 40× more CNOTs. | Choose by device error rate, not qubits |
| *Does preprocessing matter?* | Interpolation moves end-to-end PSNR by ≈ 3.4 dB. Equalisation helps contrast but costs fidelity to the source. | Classical stages still bound the result |
| *Does adding operations hurt?* | 8 inversion stages cost < 0.3 dB. State preparation dominates. | Optimise loading, not pixel ops |

Full ranking, with variance shares and p-values from a 2⁷ factorial design: **[`results/REPORT.md`](results/REPORT.md)**.

## Quick start

```bash
pip install -r requirements.txt
```

```bash
python -m qipbench demo --encoding frqi --size 4 --shots 4096
```

```bash
python -m qipbench run
```

```bash
python -m qipbench serve
```

* `demo`: one pipeline run with metrics and the circuit diagram.
* `run`: the full study (≈ 5 min on 8 cores; add `--quick` for a ≈ 1 min smoke test). It writes CSVs, figures,
  `summary.json` and `REPORT.md` to `results/`.
* `serve`: the dashboard at <http://127.0.0.1:8000>.
* `pytest`: 27 correctness tests, each checked against an exact classical answer.

## Google Colab demo

`QIP_Bench_Colab.ipynb` is a single notebook for presenting the project in Colab. It loads the project (zip upload, GitHub
or Drive) and installs Qiskit. It then runs the tests, the pipeline, the animations and the research results, and opens the
dashboard inside Colab, with a live widget panel at the end.

```bash
python -m qipbench package
```

This builds `dist/qip-bench.zip`. Upload the notebook to Colab, choose **Runtime → Run all**, and pick the zip when asked.
The step-by-step guide, a 12-minute demo script and answers to likely questions are in
[`docs/COLAB_DEMO_GUIDE.md`](docs/COLAB_DEMO_GUIDE.md).

## Jupyter visual lab

`notebooks/04_quantum_visual_lab.ipynb` brings every dashboard visual into Jupyter, powered by `qipbench/viz.py`:

| Function | What it shows |
|---|---|
| `viz.bloch_precession()` · `viz.bloch(θ, φ)` | animated / rotatable 3-D Bloch sphere |
| `viz.pipeline_strip(r)` · `viz.draw_circuit(qc)` | source → loaded → expected → reconstruction → error; the Qiskit circuit |
| `viz.pixel_scan(r)` · `viz.pixel_bloch(r)` | every pixel's FRQI qubit, as an animation and as a slider + rotatable sphere |
| `viz.shot_replay(r)` | wavefunction collapse: the real shots replayed, image decoded after each batch |
| `viz.noise_sweep()` · `viz.factor_sweep(factor, levels)` | any factor animated: noise cliff, shots, size, bit depth, operations |
| `viz.qhed_animation()` | quantum edges emerging as shots grow, with F1 vs exact and Sobel |
| `viz.factor_ranking(s)` · `viz.ofat_explorer(s)` | interactive Plotly research results with dropdowns |
| `viz.lab()` | ipywidgets control panel for every factor (needs a live kernel) |

```bash
jupyter lab notebooks/04_quantum_visual_lab.ipynb
```

Animations are embedded, so they play in the saved notebook without re-running. Use *Run All* for the live panel.

## Dashboard

| Tab | Purpose |
|---|---|
| **Overview** | Executive summary: KPI tiles, factor-influence ranking per encoding and dimension, key findings, business takeaways |
| **Quantum Lab** | Configure every factor, run the real circuit, see source → preprocessed → expected → reconstruction → error map, metrics and the circuit |
| **Compare Encodings** | FRQI vs NEQR vs QPIE on the same (uploaded) image: qubits, CNOTs, depth, PSNR, SSIM, fidelity |
| **Edge Detection** | Quantum Hadamard Edge Detection vs exact classical differences vs Sobel |
| **Research Explorer** | Interactive response curves for all 12 controlled studies, table view, and the generated figure gallery |
| **Methodology** | Pipeline, formulas, factors and responses |

## What is implemented

| Component | Implementation | Verified by |
|---|---|---|
| FRQI | H on position + uniformly controlled R_Y(2θᵢ), θᵢ = (π/2)Iᵢ. *Baseline:* multi-controlled R_Y per pixel. *Optimized:* Gray-code multiplexer, exactly 2²ⁿ CNOTs | statevector = definition; operator-equal to Qiskit `UCRYGate` |
| NEQR | q-bit grey level as a basis state via MCX. *Optimized:* Gray-order shared X-flips + one ancilla per pixel condition | exact round trip; inversion = complement |
| QPIE | amplitude encoding with classical norm side-info | exact round trip |
| QHED | amplitude encoding + ancilla, H · decrement · H, odd states give (cᵢ − cᵢ₊₁)/2, H + V scans | exact mode equals classical differences |
| Noise | depolarising (1q: p/10, CNOT: p) + readout p, after transpiling to {rz, sx, x, cx} | fidelity falls with p |
| Reconstruction | FRQI conditional / marginal estimator; NEQR majority / mean; neighbour or zero fill for unmeasured pixels | coverage tests |
| Statistics | OFAT η², full 2⁷ factorial with main effects, 21 interactions, residual share and t-tests | — |

## Project structure

```
qipbench/            core package
  images.py          sources + preprocessing (resize, normalise, quantise)
  encoders.py        FRQI, NEQR, QPIE (baseline and optimized circuits, decoders)
  backend.py         transpilation, noise model, Aer execution
  pipeline.py        end-to-end pipeline + metrics for one configuration
  edge.py            Quantum Hadamard Edge Detection
  metrics.py         PSNR, SSIM, fidelity, TVD, edge F1/IoU, entropy
  studies.py         OFAT, factorial and edge experiment definitions + parallel runner
  analysis.py        effect sizes, factorial regression, figures, summary.json
  report.py          auto-generated REPORT.md
  viz.py             notebook animations, Plotly 3-D/interactive figures, ipywidgets lab
  server.py          FastAPI service for the dashboard
  cli.py             `python -m qipbench …`
web/                 dashboard (HTML/CSS/JS, Chart.js)
notebooks/           01 encoding (A1) · 02 edge detection (A2) · 03 factor analysis (A3) · 04 visual lab, executed with outputs
results/             measured data, figures, REPORT.md (regenerated by `run`)
tests/               pytest suite
docs/                METHODOLOGY.md · PROJECT_CHARTER.md · VIVA_GUIDE.md · COLAB_DEMO_GUIDE.md · SUBMISSION_TEMPLATES.md
QIP_Bench_Colab.ipynb  one-click Colab demo notebook
```

## Course mapping

| Assessment | Evidence in this repository |
|---|---|
| **A1:** encoding and circuits | `notebooks/01_encoding_fundamentals.ipynb` (2×2 / 4×4 FRQI and NEQR, statevector checks, decoding vs shots), `docs/PROJECT_CHARTER.md` |
| **A2:** quantum-assisted operation | `notebooks/02_quantum_edge_detection.ipynb`, `qipbench/edge.py`, classical pre/post-processing and Sobel baseline |
| **A3:** full pipeline and evaluation | `python -m qipbench run`, `results/REPORT.md`, dashboard, 27 tests, `docs/METHODOLOGY.md` |
| CO1 / CO2 / CO3 | linear-algebra state checks · QHED circuits · integrated classical-quantum-classical pipeline with metrics |

## Limitations

Simulated noise is uniform depolarising + readout, and no coupling map is applied, so CNOT counts are lower
bounds for hardware. Noisy studies use ≤ 12-qubit circuits (4×4 images) because trajectory simulation
cost grows with 2^qubits × gates × shots. See *Threats to validity* in `docs/METHODOLOGY.md`.

## References

Le et al. 2011 (FRQI) · Zhang et al. 2013 (NEQR) · Yao et al. 2017 (QHED) · Möttönen et al. 2004
(uniformly controlled rotations) · Nielsen & Chuang 2010 · Gonzalez & Woods 2018.
