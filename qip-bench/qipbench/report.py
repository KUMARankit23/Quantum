"""Render results/REPORT.md, a findings report generated from the measured data."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from .analysis import ENC_LABELS
from .studies import FACTOR_LABELS, FACTORIAL_FACTORS, NOISELESS_BASE, NOISY_BASE, OFAT_STUDIES

DIM_TEXT = {
    "quality": "Quality (PSNR)",
    "efficiency": "Efficiency (CNOT count)",
    "reliability": "Reliability (PSNR spread)",
    "runtime": "Runtime",
}


def _table(df: pd.DataFrame, floatfmt: str = ".3g") -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        cells = [format(v, floatfmt) if isinstance(v, float) else str(v) for v in r]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _ranking_section(summary: dict) -> list[str]:
    out = ["## 1. Answer: what really determines performance", ""]
    rk = summary.get("rankings")
    if not rk:
        return out + ["_Factorial study not run yet (`python -m qipbench run --study factorial`)._", ""]
    out += ["Share of variance explained (main effects, 2^7 full factorial, "
            "`*` = significant at p < 0.05):", ""]
    header = "| Dimension | " + " | ".join(ENC_LABELS[e] + " — top 3 factors" for e in rk) + " |"
    out += [header, "|---|" + "---|" * len(rk)]
    for dim, text in DIM_TEXT.items():
        cells = []
        for enc in rk:
            top = rk[enc][dim][:3]
            cells.append("; ".join(f"{t['label']} {t['contribution']:.0f}%{'*' if t['p_value'] < 0.05 else ''}"
                                   for t in top))
        out.append(f"| {text} | " + " | ".join(cells) + " |")
    out += ["", "How the variance splits (main effects / two-factor interactions / higher-order + replicate noise):", ""]
    for enc in rk:
        parts = ", ".join(f"{DIM_TEXT[d].split(' (')[0]} {rk[enc][d + '_split']['main']:.0f} / "
                          f"{rk[enc][d + '_split']['two_way']:.0f} / {rk[enc][d + '_split']['higher_order']:.0f} %"
                          for d in DIM_TEXT)
        out.append(f"- **{ENC_LABELS[enc]}:** {parts}")
    out += ["", "A large interaction or higher-order share means the factor's influence depends on the other "
            "factors: performance there is a *regime* (a cliff), not a sum of independent knobs.", "",
            "Strongest interactions (factors that amplify each other):", ""]
    for enc in rk:
        for dim in ("quality", "reliability"):
            inter = rk[enc][dim + "_interactions"][:2]
            txt = ", ".join(f"{i['term'].replace(' x ', ' × ')} ({i['contribution']:.1f}%)" for i in inter)
            out.append(f"- **{ENC_LABELS[enc]} / {DIM_TEXT[dim]}:** {txt}")
    return out + [""]


def _key_findings(summary: dict) -> list[str]:
    out = ["## 2. Key findings", ""]
    ofat = pd.DataFrame(summary.get("ofat", []))
    if ofat.empty:
        return out + ["_OFAT study not run yet._", ""]

    def val(study, enc, level, col):
        r = ofat[(ofat.study == study) & (ofat.encoding == enc) & (ofat.level.astype(str) == str(level))]
        return float(r[col].iloc[0]) if len(r) else float("nan")

    f = []
    f.append(f"**Circuit structure is the largest lever on cost.** For a 4×4 image the Gray-code FRQI needs "
             f"{val('structure', 'frqi', 'optimized', 'cx'):.0f} CNOTs versus "
             f"{val('structure', 'frqi', 'baseline', 'cx'):.0f} for the naive multi-controlled version, and under "
             f"p = {NOISY_BASE.noise:g} noise PSNR rises from {val('structure', 'frqi', 'baseline', 'psnr'):.1f} dB to "
             f"{val('structure', 'frqi', 'optimized', 'psnr'):.1f} dB — the same quantum state, different engineering.")
    f.append(f"**FRQI quality is shot-limited, NEQR quality is coverage-limited.** At 8×8, FRQI PSNR goes from "
             f"{val('shots', 'frqi', 64, 'psnr'):.1f} dB (64 shots) to {val('shots', 'frqi', 16384, 'psnr'):.1f} dB "
             f"(16 384 shots); NEQR is exact as soon as every pixel is observed "
             f"(coverage {val('shots', 'neqr', 64, 'coverage'):.2f} at 64 shots → "
             f"{val('shots', 'neqr', 1024, 'coverage'):.2f} at 1 024).")
    f.append(f"**NEQR trades qubits and gates for noise robustness.** At p = 1e-3 NEQR keeps "
             f"{val('noise', 'neqr', 0.001, 'psnr'):.1f} dB (majority vote absorbs bit-flips) while FRQI falls to "
             f"{val('noise', 'frqi', 0.001, 'psnr'):.1f} dB; at p = 1e-2 the values are "
             f"{val('noise', 'neqr', 0.01, 'psnr'):.1f} dB vs {val('noise', 'frqi', 0.01, 'psnr'):.1f} dB. NEQR pays "
             f"{val('noise', 'neqr', 0.001, 'cx') / max(val('noise', 'frqi', 0.001, 'cx'), 1):.0f}× more CNOTs.")
    f.append(f"**Bit depth is free for FRQI but linear in qubits for NEQR.** FRQI stays at "
             f"{val('bit_depth', 'frqi', 8, 'qubits'):.0f} qubits for any depth; NEQR grows from "
             f"{val('bit_depth', 'neqr', 1, 'qubits'):.0f} (1 bit) to {val('bit_depth', 'neqr', 8, 'qubits'):.0f} qubits (8 bit).")
    f.append(f"**Resolution dominates end-to-end quality, not the quantum channel.** End-to-end PSNR against the "
             f"source improves from {val('image_size', 'frqi', 2, 'e2e_psnr'):.1f} dB (2×2) to "
             f"{val('image_size', 'frqi', 16, 'e2e_psnr'):.1f} dB (16×16) for FRQI with exact-quality encoding, but "
             f"at a fixed 4 096 shots FRQI channel PSNR drops to {val('image_size', 'frqi', 16, 'psnr'):.1f} dB at 16×16 "
             f"because shots per pixel fall.")
    f.append(f"**Pre-processing matters at the edges of the pipeline.** Interpolation moves end-to-end PSNR by "
             f"{_spread(ofat, 'interpolation', 'e2e_psnr'):.1f} dB; histogram equalisation lowers end-to-end PSNR "
             f"({val('normalization', 'frqi', 'equalize', 'e2e_psnr'):.1f} dB vs "
             f"{val('normalization', 'frqi', 'minmax', 'e2e_psnr'):.1f} dB with min-max) because it changes the "
             f"intensities on purpose.")
    f.append(f"**Operations are cheap compared with state preparation.** Eight inversion stages change FRQI PSNR by "
             f"{val('operations', 'frqi', 0, 'psnr') - val('operations', 'frqi', 8, 'psnr'):.2f} dB: a pixel-wise "
             f"operator is one layer, while loading the image costs hundreds of gates.")
    f.append(f"**The reconstruction estimator is a free accuracy gain.** The FRQI conditional estimator reaches "
             f"{val('estimator', 'frqi', 'conditional', 'psnr'):.1f} dB vs {val('estimator', 'frqi', 'marginal', 'psnr'):.1f} dB "
             f"for the marginal one on the same measurements; NEQR majority vote reaches "
             f"{val('estimator', 'neqr', 'majority', 'psnr'):.1f} dB vs {val('estimator', 'neqr', 'mean', 'psnr'):.1f} dB "
             f"for the mean.")
    out += [f"{i}. {t}" for i, t in enumerate(f, 1)]
    edges = pd.DataFrame(summary.get("edges", []))
    if not edges.empty:
        def ev(factor, level, col="edge_f1"):
            r = edges[(edges.factor == factor) & (edges.level.astype(str) == str(level))]
            return float(r[col].iloc[0]) if len(r) else float("nan")
        out.append(f"{len(f) + 1}. **Quantum edge detection (QHED) is exact in the infinite-shot limit** "
                   f"(F1 = {ev('shots', 'exact'):.2f}) and needs many shots on realistic images: F1 = "
                   f"{ev('shots', 256):.2f} at 256 shots, {ev('shots', 16384):.2f} at 16 384. Low-contrast edges are "
                   f"the first to disappear because their probability scales with the squared difference.")
    return out + [""]


def _spread(ofat: pd.DataFrame, study: str, col: str) -> float:
    g = ofat[ofat.study == study].groupby("level")[col].mean()
    return float(g.max() - g.min()) if len(g) else float("nan")


def _ofat_tables(summary: dict) -> list[str]:
    ofat = pd.DataFrame(summary.get("ofat", []))
    if ofat.empty:
        return []
    out = ["## 4. One-factor-at-a-time results", ""]
    for st in OFAT_STUDIES:
        g = ofat[ofat.study == st.name]
        if g.empty:
            continue
        cols = ["encoding", "level", "qubits", "cx", "depth", "psnr", "ssim", "e2e_psnr", "coverage", "success", "total_s"]
        out += [f"### {FACTOR_LABELS[st.factor]}", "", f"_{st.question}_", "",
                f"![{st.name}](figures/ofat_{st.name}.png)", "", _table(g[cols]), ""]
    return out


def write_report(summary: dict, results_dir: Path) -> Path:
    lines = [
        "# What Really Determines the Performance of a Quantum Image Processing System?",
        "",
        f"_Auto-generated by `python -m qipbench report` on {date.today():%d %b %Y} from the measured data in "
        "this folder. Every number below is reproducible with `python -m qipbench run`._",
        "",
    ]
    lines += _ranking_section(summary)
    lines += _key_findings(summary)
    lines += [
        "## 3. Experimental design", "",
        f"- **Noiseless baseline:** {NOISELESS_BASE.size}×{NOISELESS_BASE.size} px, {NOISELESS_BASE.bit_depth}-bit, "
        f"{NOISELESS_BASE.shots} shots, optimized circuits, transpiler level {NOISELESS_BASE.opt_level}.",
        f"- **Noisy baseline:** {NOISY_BASE.size}×{NOISY_BASE.size} px, {NOISY_BASE.bit_depth}-bit, "
        f"{NOISY_BASE.shots} shots, depolarising p = {NOISY_BASE.noise:g} (1q: p/10, CNOT: p, readout: p).",
        "- **Images:** camera (natural), Shepp–Logan phantom (medical), blocks (synthetic); seeds 0–2.",
        "- **Factorial:** full 2^7 design per encoding over "
        + ", ".join(f"{FACTOR_LABELS[k]} {v[0]}→{v[1]}" for k, v in FACTORIAL_FACTORS['frqi'].items())
        + " (NEQR uses 2→4 px and 2→4 bit so noisy trajectories stay tractable).",
        "- **Metrics:** PSNR/SSIM against the classically expected image (quantum-channel quality), end-to-end "
        "PSNR against the source at 64×64, Bhattacharyya fidelity of the outcome distribution, pixel coverage, "
        "CNOTs/depth after transpiling to {rz, sx, x, cx}, wall-clock time, run-to-run spread.",
        "",
    ]
    figs = summary.get("figures", [])
    for enc in ("frqi", "neqr"):
        if f"factorial_pareto_{enc}.png" in figs:
            lines += [f"![factorial {enc}](figures/factorial_pareto_{enc}.png)", ""]
    if "factorial_interactions.png" in figs:
        lines += ["![interactions](figures/factorial_interactions.png)", ""]
    for enc in ("frqi", "neqr"):
        if f"influence_heatmap_{enc}.png" in figs:
            lines += [f"![influence {enc}](figures/influence_heatmap_{enc}.png)", ""]
    lines += _ofat_tables(summary)
    if "edge_detection.png" in figs:
        lines += ["## 5. Quantum edge detection (QHED)", "", "![edges](figures/edge_detection.png)", ""]
    lines += [
        "## 6. Threats to validity", "",
        "- Simulated noise is a uniform depolarising + readout model; real devices add crosstalk, "
        "leakage and connectivity (SWAP) overhead that would further penalise deep NEQR circuits.",
        "- No coupling map is applied, so CNOT counts are lower bounds for hardware execution.",
        "- Noisy studies use 4×4 images; trajectory simulation of 15+ qubits with thousands of CNOTs is "
        "itself a practical limit worth reporting.",
        "- PSNR is capped at 60 dB for perfect reconstructions so that means remain finite.",
        "",
    ]
    path = Path(results_dir) / "REPORT.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
