# Google Colab Demo Guide

How to present QIP-Bench to faculty in Google Colab: setup, a 12-minute demo script, likely questions and a fallback plan.

---

## 1. Prepare (the day before, about 10 minutes)

### Option A: upload a zip (works without GitHub)
1. On the laptop, in the project folder:
   ```bash
   python -m qipbench package
   ```
   This creates `dist/qip-bench.zip` (≈ 20 MB) with the code, saved results, notebooks and docs.
2. Go to <https://colab.research.google.com> → **File → Upload notebook** → choose `QIP_Bench_Colab.ipynb`.
3. **Runtime → Run all.** In cell **0.1** keep `SOURCE = upload` and pick `dist/qip-bench.zip` when the file picker appears.

### Option B: GitHub (recommended for the final submission)
1. Push the project to a public GitHub repository.
2. Open `https://colab.research.google.com/github/<user>/<repo>/blob/main/QIP_Bench_Colab.ipynb`,
   or click the **Open in Colab** badge in the README.
3. In cell **0.1** set `SOURCE = github` and paste the repository URL. Then **Run all**.

### Option C: Google Drive
Copy the project folder to `MyDrive/qip-bench`. In cell **0.1** set `SOURCE = drive`, then **Run all** and allow Drive access.

### Dry run
Do one full **Run all** the day before. Setup takes about 2 minutes and the whole notebook about 5. Leave that tab open.
Colab keeps outputs, so on demo day you can scroll through results even if the Wi-Fi is slow.

---

## 2. Demo script (≈ 12 minutes)

| Time | Section | What to show | What to say |
|---|---|---|---|
| 0:00 | Title cell | the agenda table | "Problem 9 asks what really determines QIP performance. We treated every pipeline stage as an experimental factor and measured its effect." |
| 0:45 | §1 Tests | `27 passed` | "Before measuring performance we proved correctness. Every circuit is checked against an exact classical answer, including operator equality with Qiskit's own `UCRYGate`." |
| 1:30 | §2.1 Pipeline | strip of five images and metrics | Walk through preprocess → encode → measure → reconstruct. **Change the form** (e.g. `SHOTS = 64`) and re-run: PSNR drops. |
| 3:00 | §2.2 Comparison | metrics table | "FRQI uses 5 qubits, NEQR 13, QPIE 4. Qubit count alone is misleading: look at the CNOT counts and the exact-level accuracy." |
| 3:45 | §3 States | Bloch sphere, circuit, pixel scan, slider | "Each pixel is a qubit state: θ = (π/2)·I. Bright pixels point to \|1⟩." Drag the slider and rotate the sphere. |
| 5:00 | §4 Collapse | shot-replay animation | "The image is never read directly. Each shot collapses the register. These are the real measured shots replayed. Blue pixels have not been observed yet." |
| 6:15 | §5.1 Noise | noise-sweep animation | **Key finding:** "FRQI degrades gracefully. NEQR is perfect up to p ≈ 3·10⁻³ and then collapses. Choose the encoding by the device error rate." |
| 7:00 | §5.2 Structure | bar charts | **Key finding:** "Same quantum state: 16 vs 360 CNOTs, and under noise 29 dB vs 18 dB. Circuit engineering is the biggest lever." |
| 7:45 | §6 QHED | edge animation | "Quantum edge detection is exact with infinite shots. Weak edges need more shots because their probability scales with the squared difference." |
| 8:45 | §7 Results | findings + ranking dropdown | "Across ≈ 2 500 runs and a 2⁷ factorial design: noise and shots drive FRQI quality, circuit structure drives cost, and NEQR quality is a regime effect. Half its variance comes from interactions." |
| 10:00 | §8 Dashboard | dashboard iframe / new tab | Overview → Quantum Lab (live replay, qubit explorer) → Compare Encodings. |
| 11:00 | §9 Live panel | ipywidgets | Ask the faculty to pick factors and press **Run quantum pipeline**. |

---

## 3. Likely questions and short answers

| Question | Answer |
|---|---|
| Why FRQI needs 2n+1 qubits | 2n position qubits address 2²ⁿ pixels and 1 colour qubit holds the angle |
| How the optimized FRQI works | Uniformly controlled R_Y in Gray-code order. Consecutive controls differ by one bit, so each step needs one CNOT: 2²ⁿ CNOTs in total. The angles are β = Mᵀα/2ⁿ with M_xj = (−1)^popcount(x & gray(j)) |
| Why NEQR survives noise up to a point | Grey levels are basis states, so the decoder takes a majority vote per pixel. Isolated bit-flips lose the vote until noise outweighs the correct outcome |
| Why FRQI quality depends on shots | Intensity is a probability, estimated as sin²θ = n₁/(n₀+n₁). The error falls like 1/√(shots per pixel) |
| What the "expected image" is | The classical result of the same operations on the same preprocessed image. PSNR against it isolates quantum-channel error |
| How the factor ranking is computed | Full 2⁷ design (7 factors × 2 levels), regressed on coded ±1 variables. % contribution = SS_term / SS_total, with t-tests on the residual |
| Why noisy runs use 4×4 images | Trajectory simulation costs about 2^qubits × gates × shots. NEQR 8×8 means 15 qubits and 5 000+ CNOTs, over a minute per noisy run. That limit is itself an efficiency finding |
| Is this real hardware? | It is the Qiskit Aer simulator with a depolarising + readout noise model. CNOT counts carry no coupling map, so they are lower bounds for hardware |

---

## 4. Troubleshooting

| Symptom | Fix |
|---|---|
| File picker does not appear in 0.1 | Run cell 0.1 on its own, or use `SOURCE = drive` / `github` |
| `project folder with qipbench/ not found` | The zip must contain the `qipbench/` folder. Recreate it with `python -m qipbench package` |
| pip warnings in 0.2 | Harmless dependency-resolver notes. Continue if the cell prints ✅ |
| Animations show as static text | Re-run the cell, and check the cell output was not collapsed |
| Widgets in §9 do not render | Re-run cell 0.3 (it enables Colab's widget manager), then §9 |
| Dashboard iframe is blank | Click the 🔗 link above it to open it in a new tab. Colab sometimes blocks iframes in incognito windows |
| "Runtime disconnected" | **Runtime → Run all** again. The project reloads in about 2 minutes |

**Offline fallback:** `notebooks/04_quantum_visual_lab.ipynb` is saved with every animation and Plotly figure embedded. Open it locally
in Jupyter or VS Code, or upload it to Colab, and it plays without running anything. The local dashboard also works:
`python -m qipbench serve`.
