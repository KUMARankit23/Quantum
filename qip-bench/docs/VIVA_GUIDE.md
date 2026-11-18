# QIP-Bench: Complete Viva Guide

**Everything in the project explained simply: the architecture, every file, every function, every test, and the
questions your teacher is likely to ask.**

> How to use this guide: read Part A once to get the big picture. Before the viva, revise Part E (tests) and
> Part F (questions). Each section starts with a one-line "in simple words" summary and then gives the detail.

---

## Contents

- **Part A: The big picture**
  - A1. What problem are we solving?
  - A2. The answer in one paragraph
  - A3. The architecture (layers and data flow)
  - A4. Folder map
- **Part B: Quantum basics you must know**
  - B1. Qubit, superposition, measurement
  - B2. Gates used in this project
  - B3. Qiskit's qubit order (little-endian)
- **Part C: The three image encodings and edge detection**
  - C1. FRQI
  - C2. NEQR
  - C3. Amplitude encoding (QPIE)
  - C4. QHED edge detection
- **Part D: Every file and every function**
  - D1. `images.py` (preprocessing)
  - D2. `encoders.py` (FRQI, NEQR, QPIE)
  - D3. `backend.py` (simulation and noise)
  - D4. `pipeline.py` (end-to-end run)
  - D5. `edge.py` (QHED)
  - D6. `metrics.py`
  - D7. `studies.py` (the experiments)
  - D8. `analysis.py` (statistics and figures)
  - D9. `report.py`
  - D10. `server.py` (dashboard backend)
  - D11. `viz.py` (notebook visuals)
  - D12. `cli.py` and `__main__.py`
  - D13. The web dashboard (`web/`)
  - D14. Notebooks, results and docs
- **Part E: Every test explained**
- **Part F: Viva questions with answers**
- **Part G: Key numbers to remember**

---

# Part A: The big picture

## A1. What problem are we solving?

**In simple words:** People often judge a quantum image system by **one number**, usually how many qubits it
uses. Problem Statement 9 says that is not enough. Many design choices change the result. We have to find out
**which choices matter most**.

The choices (we call them **factors**) we study:

| Pipeline stage | Factor | Example values |
|---|---|---|
| Image | image size | 2×2, 4×4, 8×8, 16×16 |
| Intensity representation | bit depth | 1 to 8 bits |
| Preprocessing | resize method, normalisation | nearest/bilinear/bicubic/area; none/min-max/equalise |
| Circuit structure | naive vs optimized circuit, transpiler level | baseline/optimized; level 0–3 |
| Number of operations | how many processing steps | 0–16 inversions |
| Measurement | shots | 64 … 65 536, or exact |
| Hardware | noise level | p = 0 … 0.01 |
| Reconstruction | how we decode counts into an image | conditional/marginal, majority/mean, fill method |

We measure performance in **three separate dimensions**, because one number hides trade-offs:

| Dimension | Meaning | Main metric |
|---|---|---|
| **Quality** | How close is the output image to what it should be? | PSNR (dB), SSIM |
| **Efficiency** | How expensive is the circuit? | CNOT count, depth, qubits, time |
| **Reliability** | Does it give the same answer every run? | spread of PSNR across random seeds, success rate |

## A2. The answer in one paragraph

From about **2 500 simulated runs**:
- **Circuit structure** decides cost. The same FRQI state costs 16 CNOTs with our Gray-code circuit versus about 300+
  with the naive circuit, and under noise that is the difference between ~28 dB and ~17 dB.
- **Noise and shots** decide FRQI quality.
- **NEQR is perfect up to a noise threshold and then collapses.** About half of its quality variance comes from
  *combinations* of factors. It behaves like a "cliff", not a smooth slope.
- **Preprocessing and resolution** decide how close the result is to the *original photo*.
- **Extra operations are cheap**: loading the image costs far more than processing it.

## A3. The architecture

**In simple words:** an image goes in on the left and comes out of the quantum computer on the right. Every box
is one Python file. The experiment layer runs this pipeline thousands of times with different settings and
analyses the results.

```
                         ┌──────────────────────── qipbench/pipeline.py ────────────────────────┐
  source image  ──►  images.py  ──►  encoders.py  ──►  (operations)  ──►  backend.py  ──►  encoders.py  ──►  metrics.py
  (photo/upload)     preprocess      build circuit     X gates          simulate +       decode counts     PSNR, SSIM,
                     resize,         FRQI/NEQR/QPIE    (inversion)      measure on       back to an        fidelity...
                     normalise,                                         Qiskit Aer       image
                     quantise                                           (+ noise)
                         └──────────────────────────────────────────────────────────────────────┘
                                                        │  one run = one row of numbers
                                                        ▼
   studies.py  ── runs the pipeline thousands of times (OFAT sweeps + 2^7 factorial + edge study) ──► results/*.csv
        │
        ▼
   analysis.py ── statistics (η², factorial effects, p-values) + figures ──► results/summary.json, figures/
        │
        ▼
   report.py ── writes results/REPORT.md (the findings, generated from data)

   edge.py ── quantum edge detection (QHED), uses images.py + backend.py + metrics.py

   Presentation layer:
     server.py + web/  → interactive dashboard in the browser
     viz.py            → animations and interactive figures in Jupyter / Colab
     cli.py            → command line:  demo · run · report · serve · package
```

**Layers (from bottom to top):**

| Layer | Files | Job |
|---|---|---|
| 1. Classical image layer | `images.py` | get an image and prepare it |
| 2. Quantum layer | `encoders.py`, `edge.py`, `backend.py` | build circuits, simulate them, decode results |
| 3. Pipeline layer | `pipeline.py`, `metrics.py` | connect everything for one configuration and score it |
| 4. Experiment layer | `studies.py`, `analysis.py`, `report.py` | run controlled experiments and analyse them |
| 5. Presentation layer | `server.py`, `web/`, `viz.py`, `cli.py`, notebooks | show results to people |

## A4. Folder map

```
quantum/
├── qipbench/            ← the Python package (all logic)
│   ├── __init__.py      version number
│   ├── __main__.py      lets you run "python -m qipbench"
│   ├── images.py        image sources + preprocessing
│   ├── encoders.py      FRQI, NEQR, QPIE circuits and decoders
│   ├── backend.py       transpile, noise model, Aer simulation
│   ├── pipeline.py      one complete run + its metrics
│   ├── edge.py          quantum edge detection (QHED)
│   ├── metrics.py       PSNR, SSIM, fidelity, F1, ...
│   ├── studies.py       experiment definitions + parallel runner
│   ├── analysis.py      statistics + figures
│   ├── report.py        writes REPORT.md
│   ├── server.py        FastAPI web server for the dashboard
│   ├── viz.py           notebook animations / Plotly / widgets
│   └── cli.py           command-line commands
├── web/                 dashboard front end (index.html, app.js, quantum.js, CSS)
├── tests/test_qipbench.py   27 automated tests
├── notebooks/           01 encoding · 02 edge detection · 03 analysis · 04 visual lab
├── results/             measured data (CSV), figures, summary.json, REPORT.md
├── docs/                methodology, charter, Colab guide, this viva guide, templates
├── QIP_Bench_Colab.ipynb    one-click demo for Google Colab
├── README.md · requirements.txt · pyproject.toml
```

---

# Part B: Quantum basics you must know

## B1. Qubit, superposition, measurement

* A **qubit** is like a bit, but it can be in a mix of 0 and 1: **|ψ⟩ = a|0⟩ + b|1⟩**, where |a|² + |b|² = 1.
* **Measurement** gives 0 with probability |a|² and 1 with probability |b|² (the **Born rule**). After measuring,
  the qubit *collapses* to the result. You never see a and b directly, only the outcomes.
* **n qubits** can hold a superposition of **2ⁿ** basis states at once. That is why 2n qubits can "address"
  2²ⁿ pixels.
* **Shots** = how many times we prepare the state and measure it. More shots give better estimates of the probabilities.
  The error shrinks roughly like **1/√shots**.
* **Bloch sphere**: one qubit drawn as a point on a sphere. |0⟩ is the north pole and |1⟩ the south pole. Our FRQI pixel
  qubit `cos θ|0⟩ + sin θ|1⟩` sits at polar angle **2θ** on the sphere.

## B2. Gates used in this project

| Gate | What it does | Where we use it |
|---|---|---|
| **H** (Hadamard) | \|0⟩ → (\|0⟩+\|1⟩)/√2, an equal superposition | put all pixel positions in superposition at once; QHED ancilla |
| **X** (NOT) | flips \|0⟩ ↔ \|1⟩ | select a pixel address; invert an image |
| **R_Y(φ)** | rotates around the Y axis: \|0⟩ → cos(φ/2)\|0⟩ + sin(φ/2)\|1⟩ | FRQI stores brightness as an angle |
| **CNOT (CX)** | flips the target if the control is 1 | the main 2-qubit gate; we count it as the "cost" |
| **MCX** (multi-controlled X, Toffoli family) | flips the target only if *all* controls are 1 | NEQR writes bits into the colour register |
| **Controlled R_Y** | R_Y only when the controls match | baseline FRQI |
| **StatePreparation** | builds any given amplitude vector | amplitude encoding (QPIE) |

**Why count CNOTs?** On real hardware, 2-qubit gates are about 10× noisier than 1-qubit gates. Fewer CNOTs means
less noise and a shorter run. We transpile every circuit to the basis **{rz, sx, x, cx}** (what IBM hardware uses)
and then count CX gates.

**Transpile** = rewrite a circuit using only the hardware's basic gates, optionally optimising it (levels 0–3).

## B3. Qiskit's qubit order (little-endian)

Qiskit puts **qubit 0 on the right** of a bitstring. In this project:

```
qubits 0 … n-1        = position register (pixel index i = row × width + col)
qubits n … n+c-1      = colour register
qubits after that     = ancilla (helper) qubits
measured index = ancilla·2^(n+c) + colour·2^n + position
```

Because of this layout, a decoder can **reshape** the list of probabilities into a table
(colour × position) instead of parsing text. This is used everywhere.

---

# Part C: The three image encodings and edge detection

## C1. FRQI: Flexible Representation of Quantum Images (Le et al., 2011)

**In simple words:** each pixel's brightness becomes an **angle** on one shared "colour" qubit. The position qubits say
*which* pixel we are talking about.

$$|I\rangle = \frac{1}{\sqrt N}\sum_i (\cos\theta_i|0\rangle + \sin\theta_i|1\rangle)\otimes|i\rangle,\qquad \theta_i=\frac{\pi}{2}I_i$$

* Intensity 0 (black) → θ = 0 → pure \|0⟩. Intensity 1 (white) → θ = π/2 → pure \|1⟩.
* **Qubits:** a 2ⁿ×2ⁿ image needs 2n position qubits + 1 colour qubit = **2n + 1**. So 8×8 needs 7 qubits.
* **Circuit:** H on every position qubit (all pixels at once), then for each pixel i a rotation R_Y(2θᵢ) on the
  colour qubit *controlled by the position being i*.
* **Decoding:** measure many times and count, for each position, how often the colour was 0 (n₀) and 1 (n₁). Then
  P(1 | i) = n₁/(n₀+n₁) = sin²θ, so θ = arcsin√P and I = 2θ/π.

**Worked example (2×2 image, values 0, 1/3, 2/3, 1):**

| pixel i | I | θ = (π/2)I | colour qubit | P(colour = 1 \| i) |
|---|---|---|---|---|
| 0 | 0 | 0 | \|0⟩ | 0 |
| 1 | 1/3 | π/6 | 0.866\|0⟩ + 0.5\|1⟩ | 0.25 |
| 2 | 2/3 | π/3 | 0.5\|0⟩ + 0.866\|1⟩ | 0.75 |
| 3 | 1 | π/2 | \|1⟩ | 1 |

**Two circuit structures (same state, different cost):**

* **Baseline:** for each pixel, X-gates "select" the address i (flip the zero bits), apply a multi-controlled
  R_Y, then undo the X-gates. Easy to understand, but each multi-controlled gate becomes many CNOTs.
* **Optimized (Gray code, Möttönen 2004):** a sequence `RY(β₀) CX RY(β₁) CX …` with **exactly 2²ⁿ CNOTs**
  (one per pixel). In **Gray code** consecutive numbers differ in only one bit (0, 1, 3, 2, 6, 7, 5, 4 …), so
  each step needs just one CNOT. The rotation angles β are found from the wanted angles α by one matrix
  multiplication: **β = Mᵀα / 2ⁿ**, where M[x][j] = (−1)^(number of 1-bits in x AND gray(j)).
  Our tests prove this gives exactly the same operator as Qiskit's built-in `UCRYGate`.

## C2. NEQR: Novel Enhanced Quantum Representation (Zhang et al., 2013)

**In simple words:** the grey level is stored **as binary digits** in q colour qubits. Pixel value 13 with 4 bits is
\|1101⟩. It is a basis state, not an angle.

$$|I\rangle = \frac{1}{\sqrt N}\sum_i |C_i\rangle\otimes|i\rangle$$

* **Qubits:** 2n + q (8×8, 8-bit → 6 + 8 = 14; plus 1 ancilla in our optimized version = 15).
* **Circuit:** H on the position qubits. For every pixel and every bit that is 1, a **multi-controlled X** on that
  colour qubit, controlled by "position = i".
* **Decoding:** for each position, take the grey level seen **most often** (majority vote). Because the value is a
  basis state, **one clean observation per pixel is enough** to read it exactly.
* **Why it survives noise:** a noise bit-flip produces a *wrong* value only occasionally, so the correct value
  still wins the vote. That holds until noise becomes so strong that wrong values outnumber the right one. This
  is the **cliff** seen at p ≈ 0.01.
* **Cost:** many more CNOTs than FRQI, because multi-controlled X gates are expensive.

**Two structures:**
* **Baseline:** per pixel, X-sandwich + one MCX for each set bit.
* **Optimized:**
    1. Visit pixels in **Gray-code order**. Consecutive addresses differ in one bit, so most X-flips are shared
       instead of redone.
    2. Use **one ancilla qubit**: compute "position = i" into the ancilla once (1 MCX), copy it to every set bit
       with cheap CNOTs, then uncompute it (1 MCX). That is 2 MCX per pixel instead of one per set bit.

## C3. Amplitude encoding: QPIE

**In simple words:** the brightness values themselves become the amplitudes of the quantum state.

$$|I\rangle=\sum_i c_i|i\rangle,\qquad c_i = \frac{I_i}{\lVert I\rVert}$$

* **Fewest qubits:** only 2n (8×8 → 6 qubits).
* **Catch 1:** the measured probability is cᵢ², so you get I up to an unknown scale. You must keep the **norm
  ‖I‖ as classical side information** to rescale.
* **Catch 2:** preparing an arbitrary state needs about N CNOTs (Qiskit's `StatePreparation`).
* Inversion (1 − I) is not possible as a simple gate here, so the project raises an error for it.

## C4. QHED: Quantum Hadamard Edge Detection (Yao et al., 2017)

**In simple words:** an edge is where neighbouring pixels differ a lot. QHED computes all neighbour differences
**at once** using one extra qubit.

Steps:
1. Amplitude-encode the image on n data qubits. Add **1 ancilla** (qubit 0) in \|0⟩.
2. **H on the ancilla.** Every amplitude cᵢ is now duplicated: (cᵢ, cᵢ)/√2.
3. **Decrement D**: shift all amplitudes by one position (a cyclic −1 on the whole register). The pairs become (cᵢ, cᵢ₊₁).
4. **H on the ancilla again.** Each pair (a, b) becomes ((a+b)/√2, (a−b)/√2).
5. Now the amplitude of every **odd** basis state \|2i+1⟩ equals **(cᵢ − cᵢ₊₁)/2**, the difference between neighbours.
6. Measure. P(odd state) = (difference)²/4, so difference = 2·‖I‖·√P.
7. This gives **horizontal** differences. Run again on the **transposed** image for **vertical** differences.
   Combine them as √(h² + v²) and threshold the result to get edges.
8. Remove the false "edge" between the end of one row and the start of the next (raster wrap-around).

The **decrement** is built from a ladder of MCX gates (the "+1" circuit), inverted.
**Consequence:** a small difference has a *squared*, very small probability, so weak edges need many shots.

---

# Part D: Every file and every function

### Notation used below
* *Input → Output* describes what goes in and what comes out.
* "float image in [0, 1]" means a NumPy 2-D array where 0 = black and 1 = white.

## D1. `qipbench/images.py` (classical preprocessing)

**In simple words:** gets an image and prepares it for the quantum circuit. It is always the same chain:

`source (256×256) → grayscale → resize → normalise → quantise`

Constants: `SOURCE_RES = 256` (working size of source images), `REFERENCE_RES = 64` (size used to compare
with the original), `INTERPOLATIONS` (OpenCV resize methods), `NORMALIZATIONS = ("none", "minmax", "equalize")`,
`STANDARD_IMAGES` = camera, phantom, coins, moon (natural) + gradient, checkerboard, disk, blocks (synthetic).

| Function | What it does (simple) | Input → Output |
|---|---|---|
| `_grid(res)` | Makes x, y coordinate grids from 0 to 1, used to draw synthetic shapes | int → two arrays |
| `_synthetic(name, res)` | Draws gradient, checkerboard (4×4 tiles), disk or two blocks | name → float image |
| `_natural(name)` | Loads a real photo bundled with scikit-image (camera, phantom, coins, moon) | name → float image |
| `load_standard(name, res)` | Any named test image, centre-cropped to a square and resized to `res` | name → float image 256×256 |
| `to_unit_gray(img)` | Converts colour or uint8 images to grayscale floats in [0,1] using luminance weights 0.299R + 0.587G + 0.114B | any array → float image |
| `load_bytes(raw)` | Decodes an **uploaded file** (PNG/JPG) into a square float image | bytes → float image |
| `Preprocessed` (class) | Holds every stage: `resized`, `normalized`, `quantized` (what goes into the circuit), `levels` (integer grey levels), `reference` (original at 64×64) | container |
| `resize(img, size, interpolation)` | Shrinks the image with nearest / bilinear / bicubic / area | image → size×size image |
| `normalize(img, method)` | `none` keeps values; `minmax` stretches to 0–1; `equalize` spreads the histogram evenly | image → image |
| `quantize(img, bit_depth)` | Rounds to 2^b grey levels, e.g. 2 bits → 0, 1/3, 2/3, 1 | image → (float image, integer levels) |
| `preprocess(source, size, interpolation, normalization, bit_depth)` | Runs the whole chain. **Rejects sizes that are not a power of two**, because pixel indices must fit exactly on qubits | source → `Preprocessed` |
| `upsample(img, res)` | Enlarges a small result (bilinear) back to 64×64 so it can be compared with the original | small image → 64×64 |

**Viva point:** why must size be a power of two? With n qubits we address exactly 2ⁿ positions. A 6×6 image
(36 pixels) would leave addresses unused and break the reshape-based decoding.

## D2. `qipbench/encoders.py` (the quantum representations)

**In simple words:** turns an image into a quantum circuit, and turns measurement counts back into an image.
Every encoder class has the same four methods: `n_qubits`, `encode`, `decode`, `invert`.

### Shared helpers

| Name | What it does |
|---|---|
| `STRUCTURES = ("baseline", "optimized")` | the two circuit styles |
| `EncodedImage` (dataclass) | the result of encoding: `circuit`, `position_qubits`, `color_qubits`, `ancilla_qubits`, `side_info` (e.g. the norm for QPIE). Property `n_position` = number of position qubits |
| `gray(i)` | Gray code of i = `i XOR (i >> 1)`. Consecutive Gray codes differ in **one** bit |
| `_n_position_qubits(shape)` | log₂(number of pixels); errors if not a power of two |
| `_fill_unsampled(img, valid, method)` | Some pixels may **never be measured** (too few shots). `zero` sets them to 0. `neighbor` repeatedly fills them with the average of known neighbours, growing inward |

### `class FRQI`

| Method | What it does |
|---|---|
| `angles(img)` | θᵢ = (π/2)·Iᵢ for every pixel |
| `n_qubits(shape, …)` | 2n + 1 |
| `encode(img, bit_depth, structure)` | Builds the circuit: H on positions, then the multiplexed rotation. Uses **R_Y(2θ)**, because R_Y(φ) rotates by φ/2 in the amplitudes |
| `_multiplexed_naive(qc, angles, ctrl, target)` | **Baseline:** for each pixel, flip zero-address bits with X, apply an n-controlled R_Y, flip back. Skips pixels with angle 0 |
| `_multiplexed_gray(qc, angles, ctrl, target)` | **Optimized:** computes β = Mᵀα/2ⁿ, then applies R_Y(βⱼ) followed by one CNOT whose control is the bit that changes between gray(j) and gray(j+1) |
| `decode(dist, shape, enc, estimator, fill)` | Reshapes counts into a 2 × N table (colour 0/1 × position). **`conditional`** estimator: P(1\|i) = n₁/(n₀+n₁). **`marginal`**: uses only n₁ and the total, so it is worse because it ignores the per-pixel normalisation. Converts back with I = (2/π)·arcsin√P and returns the image and **coverage** (fraction of pixels seen) |
| `invert(qc, enc)` | One **X on the colour qubit** swaps cos and sin, so θ → π/2 − θ and I → 1 − I |

### `class NEQR`

| Method | What it does |
|---|---|
| `n_qubits` | 2n + q (+1 ancilla if optimized) |
| `encode` | Converts intensities to integers 0 … 2^q−1. **Baseline:** per pixel, X-sandwich and one MCX for every bit equal to 1. **Optimized:** visits pixels in Gray order, keeps track of which address qubits are currently flipped (`flipped` bitmask) so it only toggles what changed, and uses the ancilla trick (MCX → ancilla, CX fan-out, MCX uncompute) when a pixel has 2+ set bits |
| `decode` | Reshapes into a 2^q × N table (grey level × position). **`majority`**: most frequent level per pixel (`argmax`). **`mean`**: average level, which is badly affected by noise. Then fills unseen pixels |
| `invert` | X on **every** colour qubit: C → (2^q − 1) − C |

### `class Amplitude` (QPIE)

| Method | What it does |
|---|---|
| `n_qubits` | 2n |
| `encode` | Normalises the image vector and loads it with `StatePreparation`. Stores the norm in `side_info`. An all-black image is handled specially |
| `decode` | I = norm × √P |
| `invert` | Raises an error (not a simple unitary for this encoding) |

### Registry
`ENCODERS` maps names to objects. `get_encoder("frqi")` returns the FRQI object, or raises a clear error for an unknown name.

## D3. `qipbench/backend.py` (running circuits)

**In simple words:** takes a circuit, translates it to hardware gates, runs it on the Qiskit Aer simulator (with or
without noise), and returns the counts plus cost numbers.

| Name | What it does |
|---|---|
| `BASIS_GATES = ["rz", "sx", "x", "cx"]` | the IBM-style native gates we transpile to |
| `AER_THREADS` | how many CPU threads Aer may use (set to 1 inside parallel workers so they don't fight) |
| `ExecutionResult` (dataclass) | `distribution` (counts or exact probabilities), `exact` (ideal probabilities), shots, noise, qubits, `logical_depth` (before transpiling), `depth`, `cx`, `gates` (after transpiling), `transpile_s`, `simulate_s` (timings) |
| `noise_model(p)` | Builds the **one-knob noise model**: depolarising error p/10 on 1-qubit gates, p on CNOT, and readout flip probability p. Returns None for p = 0. Cached so it is built only once per p |
| `circuit_cost(qc, opt_level, seed)` | Transpiles to the basis gates at optimisation level 0–3 and times it |
| `exact_probabilities(qc)` | Uses Aer's statevector method with `save_probabilities` to get the exact Born-rule probabilities (the "infinite shots" answer). Much faster than Qiskit's pure-Python `Statevector` for big circuits |
| `_counts_to_vector(counts, n)` | Turns Qiskit's `{"0101": 37, …}` dictionary into a NumPy array indexed by basis state |
| `execute(qc, shots, noise, opt_level, seed)` | **The main function.** Transpile → exact probabilities → if `shots=None` return them (noise not allowed in exact mode), else add measurements and sample `shots` times on `AerSimulator` with the noise model. Seeds make runs reproducible |

**Viva point:** "depolarising error" means that with probability p the qubit's state is replaced by random noise.
"Readout error" means the measurement reports the wrong bit with probability p.

## D4. `qipbench/pipeline.py` (one complete experiment)

**In simple words:** `run(config)` is "do everything once and score it".

| Name | What it does |
|---|---|
| `QUALITY_THRESHOLD_SSIM = 0.90` | a run counts as a **success** if SSIM ≥ 0.90 |
| `PipelineConfig` (frozen dataclass) | **All factors in one object:** `encoding, image, size, bit_depth, interpolation, normalization, structure, opt_level, operations, shots, noise, estimator, fill, seed`. `with_(**kw)` returns a copy with some values changed |
| `PipelineResult` | `config, source, preprocessed, expected, reconstructed, metrics, circuit, distribution, layout`. `row()` flattens config + metrics into one dictionary (one CSV row) |
| `run(config, source=None)` | The full pipeline (steps below) |

**What `run` does, step by step:**
1. Pick the encoder and estimator (`auto` means FRQI → conditional, NEQR → majority).
2. Load the image (unless an uploaded `source` is given) and **preprocess** it.
3. **Encode** the quantized image into a circuit.
4. Add `operations` inversion stages, each separated by a **barrier**. The barrier stops the transpiler from
   cancelling X·X pairs, so each stage is a real step.
5. Compute the **expected** image classically: the quantized image, or 1 − image if the number of inversions is odd.
6. **Execute** on the simulator and **decode** to get the reconstructed image.
7. For end-to-end comparison, undo the inversion and upsample to 64×64.
8. Compute all **metrics**:

| Metric | Meaning |
|---|---|
| `qubits, logical_depth, depth, cx, gates` | circuit size and cost |
| `mse, psnr, ssim` | reconstruction vs **expected** (quantum-channel quality) |
| `level_accuracy` | fraction of pixels recovered at exactly the right grey level |
| `fidelity, tvd` | how close the measured outcome distribution is to the ideal one |
| `coverage` | fraction of pixels observed at least once |
| `e2e_psnr, e2e_ssim` | reconstruction vs the **original source** at 64×64 (end-to-end quality) |
| `preprocess_psnr` | how much quality was already lost by classical preprocessing alone |
| `entropy` | image complexity (bits) |
| `transpile_s, simulate_s, total_s` | timings |
| `shot_cost` | shots × depth (a proxy for hardware time) |
| `success` | 1 if SSIM ≥ 0.90 |

**Viva point:** why two kinds of PSNR? `psnr` isolates the **quantum** error (did the circuit reproduce what we
loaded?). `e2e_psnr` includes **classical** losses (resolution, quantisation). Mixing them would blur cause and effect.

## D5. `qipbench/edge.py` (quantum edge detection)

| Name | What it does |
|---|---|
| `increment(n)` | Circuit for \|x⟩ → \|x+1 mod 2ⁿ⟩. For each bit from the top down, flip it if all lower bits are 1 (MCX), then flip bit 0 |
| `qhed_circuit(img)` | Builds QHED: StatePreparation of the normalised image on qubits 1…n, H on ancilla 0, **decrement** (= `increment(n+1).inverse()`), H on ancilla. Returns the circuit and the norm |
| `classical_differences(img)` | The exact answer: \|I(r,c) − I(r,c+1)\| horizontally and \|I(r,c) − I(r+1,c)\| vertically |
| `sobel_edges(img)` | Standard classical Sobel operator (OpenCV), used for comparison |
| `EdgeResult` | input image, quantum horizontal/vertical/magnitude/edges, classical magnitude/edges, Sobel edges, metrics, circuit |
| `_scan(img, …)` | Runs one QHED circuit, takes the odd-state probabilities, converts them to differences (2·norm·√p), and zeroes the last column (wrap-around) |
| `detect(img, threshold, shots, noise, …)` | Horizontal scan on the image + vertical scan on its transpose. Magnitude = √(h² + v²), edges = magnitude > threshold. Metrics: gradient error, **edge F1/IoU vs exact classical edges**, F1 vs Sobel, fidelity, qubits, CNOTs |

## D6. `qipbench/metrics.py` (how we score)

| Function | Formula / meaning (simple) |
|---|---|
| `mse(ref, img)` | mean of (difference)², lower is better |
| `psnr(ref, img)` | 10·log₁₀(1/MSE) in dB, higher is better. 30 dB is good and 40+ dB is excellent. **Capped at 60 dB** (`PSNR_CAP`) for perfect results so averages stay finite |
| `ssim(ref, img)` | Structural similarity (0–1) comparing brightness, contrast and structure. For images smaller than 3×3 we use the global SSIM formula, because the usual sliding window does not fit |
| `level_accuracy(ref, img, bits)` | share of pixels exactly right at that bit depth |
| `classical_fidelity(p, q)` | Bhattacharyya fidelity (Σ√(pᵢqᵢ))²: 1 = identical distributions |
| `tvd(p, q)` | total variation distance ½Σ\|pᵢ − qᵢ\|: 0 = identical |
| `edge_scores(truth, pred)` | precision, recall, **F1**, **IoU** and pixel accuracy for binary edge maps |
| `image_entropy(img)` | Shannon entropy of the grey-level histogram, measuring image complexity |

## D7. `qipbench/studies.py` (the controlled experiments)

**In simple words:** defines *which* runs to do, and runs them in parallel on several CPU cores.

| Name | What it is |
|---|---|
| `STUDY_IMAGES = (camera, phantom, blocks)` | natural, medical and synthetic: different kinds of content |
| `SEEDS = (0, 1, 2)` | three repeats with different random seeds, to measure reliability |
| `NOISELESS_BASE` | 8×8, 8-bit, 4096 shots, no noise |
| `NOISY_BASE` | 4×4, 4-bit, 4096 shots, p = 0.001. Smaller, because noisy simulation is slow |
| `FACTOR_LABELS` | human-readable names for plots |
| `Study` (dataclass) | one OFAT study: name, factor, levels, baseline, encodings, images, seeds, overrides, research question. `configs()` produces every `PipelineConfig` (levels × images × seeds × encodings) |
| `OFAT_STUDIES` | the **12 one-factor-at-a-time studies**: image_size, bit_depth, interpolation, normalization, structure, opt_level, operations, shots, noise, estimator, fill, image |
| `FACTORIAL_FACTORS` | the 7 factors and their low/high levels for the 2⁷ design (NEQR uses smaller sizes) |
| `factorial_configs(encoding)` | all 128 combinations × images × seeds |
| `EDGE_SWEEPS`, `EDGE_BASE`, `EDGE_IMAGES` | settings for the QHED study (shots, size, noise, threshold) |
| `_edge_job`, `edge_jobs` | one QHED run, and the list of all of them |
| `_init_worker()` | runs in each worker process: limits Aer to 1 thread |
| `_pipeline_job(args)` | runs one config and returns its CSV row with study name and level |
| `_parallel(fn, jobs, workers, …)` | runs jobs in a process pool and prints progress |
| `run_ofat`, `run_factorial`, `run_edges` | run each study and return a pandas table. `quick=True` uses 1 image and 1 seed |
| `_workers()` | how many processes to use: limited by CPU **and free memory** (~0.6 GB each, because Qiskit is heavy). Too many workers crashed the machine during development |

**OFAT vs factorial, in simple words:**
* **OFAT** (one-factor-at-a-time): change one knob, keep the rest fixed. Shows the *shape* of each effect.
* **Factorial 2⁷**: try every combination of 7 knobs at two levels (128 combinations). Shows *which knob matters
  most* and whether knobs **interact**. For example, shots only matter a lot when noise is present.

## D8. `qipbench/analysis.py` (statistics and figures)

| Function | What it does |
|---|---|
| `_level_order(study, levels)` | puts levels in their natural order (2, 4, 8, 16, not "16, 2, 4, 8") |
| `eta_squared(df, factor, metric)` | **η²** = variance between levels / total variance. "What share of the variation does this factor explain?" 0 = none, 1 = everything |
| `_ci95(x)` | 95 % confidence interval half-width (t-distribution) |
| `summarize_ofat(df)` | mean PSNR, SSIM, success, CNOTs, etc. per study × encoding × level, plus CI and per-seed spread |
| `ofat_influence(df)` | η² of each factor on quality, end-to-end quality, efficiency, runtime and reliability |
| `factorial_effects(df, encoding)` | Codes each factor as −1/+1 and fits a regression with all **main effects + 21 two-factor interactions**. For each term: effect size, **% contribution** (SS_term/SS_total), p-value (t-test), plus a **residual** row (higher-order interactions + noise) |
| `rankings(effects)` | per encoding and dimension, factors sorted by % contribution, the top interactions, and the main / 2-way / higher-order split |
| `_save`, `plot_ofat`, `plot_factorial`, `plot_interactions`, `plot_influence_heatmap`, `plot_edges` | draw the PNG figures in `results/figures/` |
| `_records(df)` | converts a table to JSON-safe records |
| `analyse(results_dir)` | reads the CSVs, runs everything above, and writes `summary.json` plus all figures |

**Viva point:** why use a regression on ±1 codes? In a full 2^k design the columns are **orthogonal**, so each
effect can be estimated independently: effect = 2 × coefficient and SS = N × coefficient².

## D9. `qipbench/report.py`

| Function | What it does |
|---|---|
| `_table(df)` | turns a table into Markdown |
| `_ranking_section(summary)` | "Answer" section: top-3 factors per dimension, variance split, strongest interactions |
| `_key_findings(summary)` | writes the numbered findings **using numbers pulled from the data** (nothing is hard-coded) |
| `_spread`, `_ofat_tables` | helpers for the per-study tables |
| `write_report(summary, dir)` | assembles `REPORT.md`: answer, findings, design, figures, tables, threats to validity |

## D10. `qipbench/server.py` (dashboard backend, FastAPI)

**In simple words:** a small web server. The browser sends settings, the server runs the real quantum pipeline and
sends back images and numbers as JSON.

| Name | What it does |
|---|---|
| `MAX_QUBITS_EXACT = 18`, `MAX_QUBITS_NOISY = 12` | safety limits so a request doesn't take minutes |
| `png(img, cmap)` | turns an array into a base64 PNG (scaled up with nearest neighbour so pixels stay sharp) |
| `_source(file, image)` | uses the uploaded file (max 10 MB) or a named test image |
| `_guard(cfg)` | rejects settings that are too big or invalid with a clear message (HTTP 400) |
| `_config(...)` | builds a `PipelineConfig` from form fields (shots ≤ 0 means exact) |
| `_circuit_text(qc)` | text drawing of small circuits |
| `_measurement(r)` | sends the measured outcomes so the browser can **replay the shots** |
| `_pipeline_payload(r)` | everything the Lab tab needs: images, pixels, metrics, circuit, measurement |
| `_run_or_400` | turns a pipeline error into a friendly 400 response |
| `GET /` (`index`) | the dashboard page |
| `GET /api/meta` | available options and baselines |
| `POST /api/pipeline` | run one configuration |
| `POST /api/compare` | FRQI vs NEQR vs QPIE on the same image |
| `POST /api/edges` | QHED vs classical vs Sobel |
| `GET /api/findings` | key findings parsed from REPORT.md |
| `GET /api/results` | `summary.json` for the research charts |

## D11. `qipbench/viz.py` (notebook and Colab visuals)

| Function | What it shows |
|---|---|
| `setup()` | plot style, small JPEG animation frames, Plotly renderer (`colab` in Colab, with the widget manager enabled) |
| `_html(anim)` | turns a matplotlib animation into embedded HTML with play controls |
| `run(**kw)` | shorthand for `pipeline.run(PipelineConfig(**kw))` |
| `_encoded_stub(r)` | rebuilds the register layout so the real decoder can be reused in animations |
| `_gray(ax, img)` | small helper to draw a grayscale image |
| `pipeline_strip(r)` | source → loaded → expected → reconstruction → error map, with headline metrics |
| `draw_circuit(qc)` | Qiskit's matplotlib circuit drawing |
| `metrics_table(results)` | comparison table |
| `structure_comparison()` | bar charts: baseline vs optimized CNOTs, depth and noisy PSNR |
| `_sphere_traces`, `_vector`, `bloch(θ, φ)` | rotatable 3-D Bloch sphere (Plotly) |
| `pixel_bloch(r)` | slider over pixels: the image with the chosen pixel outlined, and that pixel's qubit on the sphere |
| `_mpl_bloch(ax)` | matplotlib Bloch sphere for animations |
| `bloch_precession()` | animation: a qubit precessing (φ turning) |
| `pixel_scan(r)` | animation: scans every pixel and shows its qubit state |
| `_replay_checkpoints`, `shot_replay(r)` | **wavefunction collapse**: replays the real shots in random order, decodes the image after each batch, and grows a histogram and a PSNR-vs-shots curve. Blue = not yet observed |
| `noise_sweep()` | animation: FRQI vs NEQR as noise increases (the cliff) |
| `factor_sweep(factor, levels)` | animation for any single factor |
| `qhed_animation()` | edges appearing as shots grow, with F1 curves |
| `load_summary`, `factor_ranking`, `ofat_explorer` | interactive Plotly research charts with dropdowns |
| `lab()` | ipywidgets control panel to run any configuration live |

## D12. `qipbench/cli.py` and `__main__.py`

`__main__.py` just calls `main()`, so `python -m qipbench …` works.

| Command | Function | What it does |
|---|---|---|
| `demo` | `_demo` | one run, prints metrics and (if small) the circuit |
| `run [--study] [--quick] [--out]` | `_run` | runs the experiments, then the report |
| `report [--out]` | `_report` | analysis + REPORT.md from existing CSVs |
| `serve` | `_serve` | starts the dashboard with uvicorn |
| `package` | `_package` | zips the project into `dist/qip-bench.zip` for Colab |

## D13. The web dashboard (`web/`)

| File | Job |
|---|---|
| `index.html` | page structure: the 6 tabs (Overview, Quantum Lab, Compare, Edge Detection, Research Explorer, Methodology) |
| `styles.css` | layout and colours, light/dark mode |
| `quantum.css` | animations: hero circuit pulses, stage stepper, glow, scan reveal, and a reduced-motion switch-off |
| `app.js` | talks to the API (`fetch`), fills tiles and tables, draws Chart.js charts, handles forms |
| `quantum.js` | `background` (particle "qubits" with entanglement lines), `Bloch` (draggable sphere drawn on canvas), `Replay` (shot replay and decoding in JavaScript), `countUp`, `stages` (progress stepper) |

## D14. Notebooks, results and docs

| Item | Purpose |
|---|---|
| `notebooks/01_encoding_fundamentals.ipynb` | **A1**: 2×2 and 4×4 FRQI/NEQR, statevector checks, decoding vs shots |
| `notebooks/02_quantum_edge_detection.ipynb` | **A2**: QHED step by step, shots and noise |
| `notebooks/03_performance_factor_analysis.ipynb` | **A3**: rankings, interactions, response curves |
| `notebooks/04_quantum_visual_lab.ipynb` | all animations and interactive visuals |
| `QIP_Bench_Colab.ipynb` | the Colab demo |
| `results/*.csv` | raw data: `ofat.csv` (858 runs), `factorial.csv` (1 536), `edges.csv` (171) |
| `results/summary.json`, `figures/`, `REPORT.md` | analysis outputs |
| `docs/METHODOLOGY.md` | research design, hypotheses, threats to validity |
| `docs/PROJECT_CHARTER.md` | objectives, scope, timeline, roles |

---

# Part E: Every test explained

**How to run:** `python -m pytest -q`. Result: **27 passed** in about 5 seconds.

**Why tests matter for the viva:** they *prove* the quantum parts are correct. Each test compares the quantum
result with an **exact classical answer** that we know is right.

**Shared setup at the top of the file:**
```python
RNG = np.random.default_rng(7)            # fixed seed → same random images every time

def random_image(size, bits=8):
    return np.rint(RNG.random((size, size)) * (2 ** bits - 1)) / (2 ** bits - 1)
```
`random_image` makes a random image whose values are already exact grey levels (e.g. k/255). This means the
round trip can be checked exactly, with no rounding surprises.

**Why are there 27 tests?** There are 16 test functions. The first one is *parametrized*: it runs for 3 encodings × 2
structures × 2 sizes = 12 cases. 12 + 15 = 27.

---

### Test 1: `test_exact_roundtrip` (12 cases)

```python
@pytest.mark.parametrize("enc", [FRQI(), NEQR(), Amplitude()])
@pytest.mark.parametrize("structure", ["baseline", "optimized"])
@pytest.mark.parametrize("size", [2, 4])
def test_exact_roundtrip(enc, structure, size):
    img = random_image(size)
    e = enc.encode(img, 8, structure)
    res = execute(e.circuit, shots=None)
    rec, coverage = enc.decode(res.distribution, img.shape, e)
    assert np.allclose(rec, img, atol=1e-9)
    assert res.qubits == enc.n_qubits(img.shape, 8, structure)
```

**What it checks:** encode an image → simulate with **exact probabilities** (no sampling noise) → decode →
we must get back **exactly the same image**. It also checks that the circuit uses the number of qubits the formula
promises (2n+1 for FRQI, 2n+q(+1) for NEQR, 2n for QPIE).

**Line by line:**
1. The decorators run the test for every combination of encoding, structure and size.
2. Make a random 2×2 or 4×4 image.
3. Build the circuit.
4. `shots=None` → exact Born-rule probabilities.
5. Decode the probabilities into an image.
6. `allclose(..., atol=1e-9)`: the images match to 9 decimal places.
7. The qubit count matches the theory.

**If asked "what does this prove?":** the encoder and decoder are exact inverses, for *both* circuit designs and
*all three* encodings. Any error seen later must therefore come from **finite shots or noise**, not from bugs.

---

### Test 2: `test_frqi_state_matches_definition`

```python
def test_frqi_state_matches_definition():
    img = random_image(2)
    e = FRQI().encode(img, structure="optimized")
    theta = (np.pi / 2) * img.ravel()
    expected = np.concatenate([np.cos(theta), np.sin(theta)]) / 2
    assert np.allclose(Statevector(e.circuit).data.real, expected, atol=1e-9)
```

**What it checks:** the quantum state from our circuit equals the **FRQI formula from the paper**.

**How:** for a 2×2 image (N = 4) the formula says the amplitude of \|colour=0, position=i⟩ is cos θᵢ/2 and of
\|colour=1, i⟩ is sin θᵢ/2 (the 1/2 is 1/√4). Because colour is the higher qubit, the first 4 amplitudes are the cos
terms and the next 4 the sin terms, so we concatenate them. `Statevector` computes the circuit's exact state, and
we compare.

**Difference from test 1:** test 1 checks *probabilities* after decoding. This test checks the *actual amplitudes*,
including signs, so it is a stricter check of the state preparation.

---

### Test 3: `test_gray_code_multiplexor_equals_qiskit_ucry`

```python
def test_gray_code_multiplexor_equals_qiskit_ucry():
    angles = RNG.random(8) * np.pi
    ours = QuantumCircuit(4)
    FRQI._multiplexed_gray(ours, angles, [0, 1, 2], 3)
    ref = QuantumCircuit(4)
    ref.append(UCRYGate(list(angles)), [3, 0, 1, 2])
    assert Operator(ours).equiv(Operator(ref))
```

**What it checks:** our hand-written Gray-code circuit is the **same unitary matrix** as Qiskit's official
uniformly controlled R_Y gate (`UCRYGate`), for 8 random angles and 3 control qubits.

**How:** `Operator(...)` turns each circuit into its full 16×16 matrix. `.equiv` checks they are equal (allowing a
global phase, which has no physical meaning). In `UCRYGate`, the target is listed first, then the controls.

**Why it matters:** this proves our optimisation is **mathematically exact** for *every possible input state*,
not just for the images we tried. It is the strongest test in the project.

---

### Test 4: `test_structures_prepare_identical_states`

```python
def test_structures_prepare_identical_states():
    img = random_image(4)
    for enc in (FRQI(), NEQR()):
        a = Statevector(enc.encode(img, 8, "baseline").circuit).probabilities()
        b = Statevector(enc.encode(img, 8, "optimized").circuit).probabilities()
        b = b.reshape(-1, a.size).sum(axis=0)
        assert np.allclose(a, b, atol=1e-9)
```

**What it checks:** baseline and optimized circuits produce the **same quantum state** for FRQI and NEQR.

**The reshape line:** optimized NEQR has one extra ancilla qubit, so its probability list is twice as long. The
ancilla is always back in \|0⟩, so we add up ("marginalise") over it before comparing.

**Why it matters:** the "circuit structure" factor is a **fair experiment**. Any quality difference between
structures is caused by **cost and noise**, not by encoding a different image.

---

### Test 5: `test_optimized_frqi_uses_exactly_n_pixels_cnots`

```python
def test_optimized_frqi_uses_exactly_n_pixels_cnots():
    for size in (2, 4, 8):
        res = execute(FRQI().encode(random_image(size), structure="optimized").circuit, shots=None, opt_level=0)
        assert res.cx == size * size
```

**What it checks:** the theory says the Gray-code multiplexer uses exactly **one CNOT per pixel** (2²ⁿ). For 2×2,
4×4 and 8×8 we count the CNOTs after transpiling and expect 4, 16 and 64.

**Why `opt_level=0`?** So the transpiler does not optimise anything away. We measure the circuit exactly as designed.

---

### Test 6: `test_neqr_inversion_is_complement`

```python
def test_neqr_inversion_is_complement():
    img = random_image(4, bits=4)
    enc = NEQR()
    e = enc.encode(img, 4)
    enc.invert(e.circuit, e)
    rec, _ = enc.decode(execute(e.circuit, shots=None).distribution, img.shape, e)
    assert np.allclose(rec, 1 - img)
```

**What it checks:** applying X to every colour qubit gives the **negative image** (1 − I).

**Why it works:** flipping every bit of a 4-bit number C gives 15 − C, and 15 − C divided by 15 is 1 − C/15.

**Why it matters:** this is a real *quantum image operation* (course topic "pixel-wise operators"), and it is the
operation used for the "number of operations" factor.

---

### Test 7: `test_gray_code_adjacent_differ_by_one_bit`

```python
def test_gray_code_adjacent_differ_by_one_bit():
    assert all(bin(gray(i) ^ gray(i + 1)).count("1") == 1 for i in range(255))
```

**What it checks:** the defining property of Gray code. For every i from 0 to 254, gray(i) XOR gray(i+1) has exactly
**one** 1-bit, so neighbours differ in exactly one position.

**Why it matters:** both optimized circuits rely on this property. One changed bit means one CNOT in FRQI, and one
shared X-flip in NEQR.

---

### Test 8: `test_unsampled_pixels_are_filled`

```python
def test_unsampled_pixels_are_filled():
    cfg = PipelineConfig(encoding="neqr", size=8, bit_depth=4, shots=16, fill="neighbor")
    r = run(cfg)
    assert r.metrics["coverage"] < 1
    assert np.isfinite(r.reconstructed).all()
```

**What it checks:** with only **16 shots for 64 pixels**, some pixels are never measured (coverage < 1). Even then,
the reconstruction must be a complete, valid image with no NaN or infinite values, because the neighbour fill
handles the gaps.

**Why it matters:** this is the "coverage" problem of basis encodings. It shows the reconstruction stage handles
it without crashing.

---

### Test 9: `test_more_shots_improve_frqi`

```python
def test_more_shots_improve_frqi():
    low = np.mean([run(PipelineConfig(shots=128, seed=s)).metrics["psnr"] for s in range(3)])
    high = np.mean([run(PipelineConfig(shots=16384, seed=s)).metrics["psnr"] for s in range(3)])
    assert high > low + 5
```

**What it checks:** FRQI quality is **shot-limited**. The average PSNR over 3 seeds with 16 384 shots must be at
least **5 dB better** than with 128 shots.

**Why average 3 seeds?** A single run is random. Averaging makes the test stable rather than flaky.

**Theory behind it:** 128× more shots should reduce the error by about √128 ≈ 11×, roughly +21 dB, so a 5 dB margin is safe.

---

### Test 10: `test_noise_reduces_distribution_fidelity`

```python
def test_noise_reduces_distribution_fidelity():
    clean = run(PipelineConfig(size=4, noise=0.0)).metrics["fidelity"]
    noisy = run(PipelineConfig(size=4, noise=1e-2, structure="baseline")).metrics["fidelity"]
    assert noisy < clean
```

**What it checks:** the noise model really does something. With p = 0.01 on the CNOT-heavy baseline circuit, the
measured distribution moves away from the ideal one, so fidelity drops.

**Why it matters:** it confirms the noise factor is "wired in". Without this test, a broken noise model would silently
give perfect results.

---

### Test 11: `test_operations_parity`

```python
def test_operations_parity():
    even = run(PipelineConfig(size=4, shots=None, operations=2))
    odd = run(PipelineConfig(size=4, shots=None, operations=3))
    assert np.allclose(even.reconstructed, even.preprocessed.quantized, atol=1e-9)
    assert np.allclose(odd.reconstructed, 1 - odd.preprocessed.quantized, atol=1e-9)
```

**What it checks:** inverting twice returns the original image (X·X = identity), and inverting three times gives the
negative image. This tests the whole pipeline end to end, in exact mode.

**Why it matters:** it shows the "number of operations" experiment is correct. In the ideal case only the parity
matters, so any loss seen in the noisy study is **caused by noise accumulating per stage**.

---

### Test 12: `test_decrement_circuit`

```python
def test_decrement_circuit():
    dec = edge.increment(3).inverse()
    for x in range(8):
        sv = Statevector.from_int(x, 8).evolve(dec)
        assert np.argmax(sv.probabilities()) == (x - 1) % 8
```

**What it checks:** the decrement circuit used inside QHED maps every 3-qubit basis state \|x⟩ to \|x − 1⟩, with
wrap-around (0 → 7).

**How:** for each x from 0 to 7, start in \|x⟩ (`from_int`), run the circuit (`evolve`), and check that the most likely
output is x − 1 mod 8.

---

### Test 13: `test_qhed_exact_equals_classical_differences`

```python
def test_qhed_exact_equals_classical_differences():
    img = images.preprocess(images.load_standard("phantom"), 8).quantized
    r = edge.detect(img, shots=None)
    assert np.allclose(r.magnitude, r.classical_magnitude, atol=1e-9)
    assert r.metrics["edge_f1"] == 1.0
```

**What it checks:** with exact probabilities, quantum edge detection gives **exactly** the classical gradient on a
real medical-phantom image, and the edge map matches perfectly (F1 = 1).

**Why it matters:** this proves our QHED implementation, including the ancilla trick, the decrement and the
wrap-around fix, is correct. So any edge errors in the experiments come **only from finite shots or noise**.

---

### Test 14: `test_quantize_levels`

```python
def test_quantize_levels():
    q, lv = images.quantize(np.linspace(0, 1, 11), 2)
    assert set(lv) <= {0, 1, 2, 3} and q.min() == 0 and q.max() == 1
```

**What it checks:** 2-bit quantisation produces only the 4 levels 0–3, and the float version still spans exactly
0 to 1.

---

### Test 15: `test_preprocess_rejects_non_power_of_two`

```python
def test_preprocess_rejects_non_power_of_two():
    with pytest.raises(ValueError):
        images.preprocess(images.load_standard("camera"), 6)
```

**What it checks:** asking for a 6×6 image raises a clear `ValueError` instead of silently building a broken
circuit. 6×6 = 36 pixels, which is not a power of two, so it cannot map onto position qubits.

---

### Test 16: `test_metrics_basics`

```python
def test_metrics_basics():
    a = random_image(8)
    assert metrics.psnr(a, a) == metrics.PSNR_CAP
    assert metrics.ssim(a, a) == pytest.approx(1.0)
    assert metrics.ssim(a[:2, :2], a[:2, :2]) == pytest.approx(1.0)
    assert metrics.classical_fidelity(np.array([.5, .5]), np.array([.5, .5])) == pytest.approx(1.0)
    s = metrics.edge_scores(np.eye(4, dtype=bool), np.eye(4, dtype=bool))
    assert s["f1"] == 1.0 and s["iou"] == 1.0
```

**What it checks:** each metric gives its "perfect" value when two inputs are identical:
* PSNR of an image with itself = the 60 dB cap
* SSIM = 1, including the special 2×2 path
* fidelity of identical distributions = 1
* F1 and IoU of identical edge maps = 1

This is a sanity check that the scoring itself is correct.

---

### Summary table of tests

| # | Test | Area | Proves |
|---|---|---|---|
| 1 | exact_roundtrip (×12) | encoders | encode/decode are exact inverses; qubit formula is right |
| 2 | frqi_state_matches_definition | FRQI | amplitudes equal the paper's formula |
| 3 | gray_code_multiplexor_equals_qiskit_ucry | FRQI optimized | our circuit = Qiskit's UCRYGate (exact unitary) |
| 4 | structures_prepare_identical_states | structure factor | baseline and optimized give the same state |
| 5 | optimized_frqi_uses_exactly_n_pixels_cnots | cost | CNOTs = number of pixels |
| 6 | neqr_inversion_is_complement | operations | X on colour qubits = negative image |
| 7 | gray_code_adjacent_differ_by_one_bit | math helper | Gray-code property |
| 8 | unsampled_pixels_are_filled | reconstruction | missing pixels handled |
| 9 | more_shots_improve_frqi | measurement | quality is shot-limited |
| 10 | noise_reduces_distribution_fidelity | noise | the noise model works |
| 11 | operations_parity | pipeline | X·X = I end to end |
| 12 | decrement_circuit | QHED | decrement unitary is correct |
| 13 | qhed_exact_equals_classical_differences | QHED | quantum edges = classical edges exactly |
| 14 | quantize_levels | preprocessing | quantisation levels |
| 15 | preprocess_rejects_non_power_of_two | preprocessing | input validation |
| 16 | metrics_basics | metrics | metrics give correct perfect scores |

---

# Part F: Viva questions with answers

### Concepts

**Q: What is quantum image processing?**
A: Representing an image as a quantum state, processing it with quantum gates and reading it back by measurement. The
hope is that some operations, such as edge detection over all pixels, can be done in superposition.

**Q: Why does FRQI need only one colour qubit?**
A: The brightness of every pixel is an *angle* on the same colour qubit. The position register says which pixel each
angle belongs to. The two registers are entangled, so each position carries its own angle.

**Q: Why R_Y(2θ) and not R_Y(θ)?**
A: R_Y(φ) produces cos(φ/2)\|0⟩ + sin(φ/2)\|1⟩. To get cos θ and sin θ we need φ = 2θ.

**Q: Why θ = (π/2)·I?**
A: It maps intensity 0…1 onto 0…π/2, so black is \|0⟩, white is \|1⟩, and every value in between has a unique angle.

**Q: FRQI vs NEQR: which is better?**
A: It depends on the noise and the measurement budget, and that is our main finding. FRQI uses few qubits and gates
but its quality depends on shots and degrades smoothly with noise. NEQR uses many more qubits and CNOTs but reads
exactly and resists noise up to a threshold, then collapses.

**Q: What is a Gray code and why use it?**
A: An ordering of binary numbers where neighbours differ in one bit. In FRQI it lets each rotation step use one CNOT
(2²ⁿ total). In NEQR it lets consecutive pixels share most of their X-flips.

**Q: What is an ancilla qubit?**
A: A helper qubit that starts and ends in \|0⟩. In NEQR it stores "is the position equal to i?" once, so we don't
repeat an expensive multi-controlled gate for every bit. In QHED it creates the pairs whose difference gives the edges.

**Q: What does transpiling do?**
A: Rewrites the circuit using only the hardware's native gates {rz, sx, x, cx}, and can optimise it (levels 0–3).
We count CNOTs after transpiling because that reflects real hardware cost.

**Q: What is a shot?**
A: One run of the circuit followed by measurement. It gives one bitstring. Probabilities are estimated from many shots.

**Q: Why does the measured image differ from the original even without noise?**
A: Finite shots. Probabilities are *estimated* from counts, so there is statistical error of about 1/√(shots per pixel).

**Q: What is coverage?**
A: The fraction of pixels observed at least once. With few shots some pixels are never sampled, so we have to fill them.

### Methodology

**Q: Why two baselines (8×8 noiseless and 4×4 noisy)?**
A: Noisy simulation follows every shot separately, so its cost grows with 2^qubits × gates × shots. NEQR 8×8 has 15
qubits and 5 000+ CNOTs, which takes over a minute per noisy run. Using 4×4 keeps thousands of runs feasible. This
limit is itself an efficiency finding.

**Q: What is OFAT and what is a factorial design?**
A: OFAT changes one factor at a time and shows the shape of each effect. A 2⁷ full factorial tests all 128
combinations of 7 factors at two levels each. It ranks the factors and reveals interactions.

**Q: What is an interaction?**
A: When the effect of one factor depends on another. For example, extra shots help a lot without noise but much less
when noise dominates (shots × noise interaction).

**Q: What does "% of variance explained" mean?**
A: Of all the variation in the results, the share caused by changing that factor. It is SS_factor / SS_total.

**Q: How do you know an effect is real and not chance?**
A: Repeated runs with different seeds give an error estimate. A t-test then gives a p-value, and p < 0.05 is marked significant.

**Q: How did you make results reproducible?**
A: Every run has a fixed seed for both the transpiler and the simulator, library versions are pinned, and
`python -m qipbench run` regenerates every CSV, figure and the report.

**Q: What are the limitations?**
A: Simulated uniform noise (real chips also have crosstalk and leakage). No hardware connectivity map, so CNOT counts
are lower bounds. Small images. PSNR is capped at 60 dB.

### Implementation

**Q: How do you decode without parsing bitstrings?**
A: Qubit 0 is the least significant bit and positions use the lowest qubits. So index = colour·N + position, and a
reshape of the probability vector to (colour, position) gives the count table directly.

**Q: Why put barriers between operations?**
A: Otherwise the transpiler would cancel X·X pairs and the "number of operations" factor would do nothing.
Barriers model separate processing stages.

**Q: Why cap PSNR at 60 dB?**
A: A perfect reconstruction has infinite PSNR, which would break averages and statistics.

**Q: How is quantum edge detection checked?**
A: In exact mode it equals the classical neighbour differences exactly (test 13). With shots we report the edge-map F1
against those exact differences, and against Sobel for context.

**Q: Why did you use Aer for exact probabilities instead of Statevector?**
A: For a 15-qubit circuit with thousands of gates, Aer's C++ statevector took 0.4 s versus 8.8 s for Qiskit's Python
`Statevector`.

**Q: What does the dashboard's "shot replay" show?**
A: The real measured outcomes, replayed in random order. After each batch the image is decoded the same way as in
Python, which shows the image appearing as the wavefunction is repeatedly collapsed.

---

# Part G: Key numbers to remember

| Fact | Number |
|---|---|
| Total simulated runs | ≈ 2 500 (858 OFAT + 1 536 factorial + 171 edge) |
| Tests | 27 passing (16 test functions) |
| FRQI qubits | 2n + 1 (4×4 → 5, 8×8 → 7) |
| NEQR qubits | 2n + q (+1 ancilla optimized) (4×4, 4-bit → 8/9; 8×8, 8-bit → 14/15) |
| QPIE qubits | 2n (8×8 → 6) |
| FRQI 4×4 CNOTs | optimized 16 vs baseline ≈ 300–380 |
| FRQI 4×4 PSNR at p = 10⁻³ | optimized ≈ 28 dB vs baseline ≈ 17 dB |
| NEQR cliff | perfect up to p ≈ 3·10⁻³, collapses at p = 10⁻² |
| FRQI 8×8 PSNR | ≈ 11 dB at 64 shots → ≈ 36 dB at 16 384 shots |
| QHED | F1 = 1.0 exact; ≈ 0.92 at 16 384 shots; ≈ 0.34 at 256 shots |
| Top FRQI quality drivers | noise ≈ 36 %, shots ≈ 28 % of variance |
| Top FRQI cost driver | circuit structure ≈ 78 % of CNOT variance |
| NEQR quality variance | ≈ 50 % from higher-order interactions (regime / cliff behaviour) |
| Noise model | 1-qubit gates p/10 · CNOT p · readout p |

**One-sentence answer for the viva:**
> "The performance of a quantum image-processing system is determined less by qubit count than by **how the circuit
> is built**, **how many measurements you take**, and **how much noise the hardware has**, and these factors interact,
> so encoding choice must match the noise regime."
