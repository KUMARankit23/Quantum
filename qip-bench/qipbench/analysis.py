"""Statistical analysis of the experiments: effect sizes, factorial effects, rankings, figures.

Three performance dimensions are scored separately, because a single number hides trade-offs:

    Quality      PSNR / SSIM of the reconstruction against the classically expected image
    Efficiency   CNOT count, transpiled depth, qubits, wall-clock time
    Reliability  run-to-run spread (std of PSNR across seeds) and success rate (SSIM >= 0.90)

Influence measures
    OFAT       eta^2 = SS_between_levels / SS_total  (share of variance explained by the factor)
    Factorial  % contribution = SS_effect / SS_total from a regression on coded (-1/+1) factors
               with all main effects and two-factor interactions; t-tests use the residual error.
"""

from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

import sys

import matplotlib

if "ipykernel" not in sys.modules:          # headless for the CLI; keep Jupyter's inline backend
    matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402

from .studies import EDGE_SWEEPS, FACTOR_LABELS, FACTORIAL_FACTORS, OFAT_STUDIES  # noqa: E402

ENC_COLORS = {"frqi": "#2a78d6", "neqr": "#eb6834", "amplitude": "#1baf7a"}   # validated CVD-safe slots 1-3
ENC_LABELS = {"frqi": "FRQI", "neqr": "NEQR", "amplitude": "Amplitude (QPIE)"}
DIMENSIONS = {
    "quality": ("psnr", "PSNR (dB)"),
    "efficiency": ("log_cx", "log10 CNOT count"),
    "reliability": ("psnr_sd", "PSNR std across seeds (dB)"),
}

plt.rcParams.update({
    "figure.dpi": 110, "savefig.dpi": 150, "font.size": 10, "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.alpha": 0.25, "axes.titleweight": "bold",
})


# ============================================================ helpers

def _level_order(study_name: str, levels) -> list:
    st = next((s for s in OFAT_STUDIES if s.name == study_name), None)
    if st is None:
        return sorted(levels, key=str)
    declared = []
    src = st.levels.values() if isinstance(st.levels, dict) else [st.levels]
    for lv in src:
        declared += ["exact" if x is None else str(x) for x in lv]
    levels = [str(x) for x in levels]
    seen = [x for x in dict.fromkeys(declared) if x in set(levels)]
    return seen + [x for x in levels if x not in seen]


def eta_squared(df: pd.DataFrame, factor: str, metric: str) -> float:
    d = df[[factor, metric]].dropna()
    if d[metric].nunique() <= 1:
        return 0.0
    grand = d[metric].mean()
    ss_tot = ((d[metric] - grand) ** 2).sum()
    ss_b = sum(len(g) * (g.mean() - grand) ** 2 for _, g in d.groupby(factor)[metric])
    return float(ss_b / ss_tot) if ss_tot > 0 else 0.0


def _ci95(x: pd.Series) -> float:
    n = x.count()
    return float(stats.t.ppf(0.975, n - 1) * x.std(ddof=1) / np.sqrt(n)) if n > 1 else 0.0


# ============================================================ OFAT

def summarize_ofat(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["level"] = df["level"].astype(str)
    g = df.groupby(["study", "encoding", "level"])
    out = g.agg(psnr=("psnr", "mean"), ssim=("ssim", "mean"), e2e_psnr=("e2e_psnr", "mean"),
                fidelity=("fidelity", "mean"), coverage=("coverage", "mean"),
                success=("success", "mean"), qubits=("qubits", "mean"), cx=("cx", "mean"),
                depth=("depth", "mean"), total_s=("total_s", "mean"), n=("psnr", "size"))
    out["psnr_ci"] = g["psnr"].apply(_ci95)
    out["psnr_sd"] = df.groupby(["study", "encoding", "level", "image"])["psnr"].std(ddof=0) \
        .groupby(["study", "encoding", "level"]).mean()
    return out.reset_index()


def ofat_influence(df: pd.DataFrame) -> pd.DataFrame:
    """Per study and encoding: share of variance each dimension's metric attributes to the factor."""
    rows = []
    d = df.copy()
    d["level"] = d["level"].astype(str)
    d["log_cx"] = np.log10(d["cx"] + 1)
    for (study, enc), g in d.groupby(["study", "encoding"]):
        sd = g.groupby(["level", "image"])["psnr"].std(ddof=0).reset_index(name="psnr_sd")
        rows.append({
            "study": study, "encoding": enc, "factor": g["factor"].iloc[0],
            "quality_eta2": eta_squared(g, "level", "psnr"),
            "ssim_eta2": eta_squared(g, "level", "ssim"),
            "e2e_eta2": eta_squared(g, "level", "e2e_psnr"),
            "efficiency_eta2": eta_squared(g, "level", "log_cx"),
            "time_eta2": eta_squared(g.assign(lt=np.log10(g["total_s"])), "level", "lt"),
            "reliability_eta2": eta_squared(sd, "level", "psnr_sd"),
            "psnr_range": float(np.ptp(g.groupby("level")["psnr"].mean().to_numpy())),
            "cx_ratio": float(g.groupby("level")["cx"].mean().max() / max(g.groupby("level")["cx"].mean().min(), 1)),
        })
    return pd.DataFrame(rows)


# ============================================================ factorial

def factorial_effects(df: pd.DataFrame, encoding: str) -> pd.DataFrame:
    factors = FACTORIAL_FACTORS[encoding]
    d = df[df["encoding"] == encoding].copy()
    for f, (lo, hi) in factors.items():
        d[f + "_c"] = np.where(d[f].astype(str) == str(hi), 1.0, -1.0)
    d["log_cx"] = np.log10(d["cx"] + 1)
    d["log_time"] = np.log10(d["total_s"])
    keys = [f + "_c" for f in factors]
    sd = d.groupby(keys + ["image"])["psnr"].std(ddof=0).reset_index(name="psnr_sd")

    responses = {"psnr": d, "ssim": d, "log_cx": d, "log_time": d, "psnr_sd": sd}
    terms = [(f,) for f in factors] + list(combinations(factors, 2))
    rows = []
    for resp, data in responses.items():
        y = data[resp].to_numpy(float)
        cols = [np.ones(len(data))]
        for t in terms:
            cols.append(np.prod([data[f + "_c"].to_numpy() for f in t], axis=0))
        X = np.column_stack(cols)
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        resid = y - X @ beta
        dof = max(len(y) - X.shape[1], 1)
        mse_res = float(resid @ resid / dof)
        ss_tot = float(((y - y.mean()) ** 2).sum())
        if ss_tot < 1e-12:                                 # response constant across the design
            rows += [{"encoding": encoding, "response": resp, "term": " x ".join(t), "order": len(t),
                      "effect": 0.0, "contribution": 0.0, "p_value": 1.0} for t in terms]
            continue
        for j, t in enumerate(terms, 1):
            ss = len(y) * beta[j] ** 2                    # orthogonal ±1 design
            se = np.sqrt(mse_res / len(y)) if mse_res > 0 else 1e-300
            tval = beta[j] / se
            rows.append({
                "encoding": encoding, "response": resp, "term": " x ".join(t),
                "order": len(t), "effect": 2 * beta[j], "contribution": 100 * ss / ss_tot,
                "p_value": float(2 * stats.t.sf(abs(tval), dof)) if mse_res > 1e-12 else 1.0,
            })
        rows.append({"encoding": encoding, "response": resp, "term": "residual", "order": 3,
                     "effect": 0.0, "contribution": 100 * float(resid @ resid) / ss_tot, "p_value": 1.0})
    return pd.DataFrame(rows)


def rankings(effects: pd.DataFrame) -> dict:
    """Per encoding and dimension, factors ordered by main-effect % contribution."""
    resp_for = {"quality": "psnr", "efficiency": "log_cx", "reliability": "psnr_sd", "runtime": "log_time"}
    out = {}
    for enc, g in effects.groupby("encoding"):
        out[enc] = {}
        for dim, resp in resp_for.items():
            m = g[(g.response == resp) & (g.order == 1)].sort_values("contribution", ascending=False)
            out[enc][dim] = [{"factor": r.term, "label": FACTOR_LABELS.get(r.term, r.term),
                              "contribution": round(r.contribution, 2), "effect": round(r.effect, 4),
                              "p_value": r.p_value} for r in m.itertuples()]
            inter = g[(g.response == resp) & (g.order == 2)].sort_values("contribution", ascending=False).head(3)
            out[enc][dim + "_interactions"] = [{"term": r.term, "contribution": round(r.contribution, 2),
                                                "effect": round(r.effect, 4)} for r in inter.itertuples()]
            sums = g[g.response == resp].groupby("order")["contribution"].sum()
            out[enc][dim + "_split"] = {"main": round(sums.get(1, 0), 1), "two_way": round(sums.get(2, 0), 1),
                                        "higher_order": round(sums.get(3, 0), 1)}
    return out


# ============================================================ figures

def _save(fig, path: Path):
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def plot_ofat(summary: pd.DataFrame, outdir: Path) -> list[str]:
    files = []
    for study, g in summary.groupby("study"):
        st = next(s for s in OFAT_STUDIES if s.name == study)
        order = _level_order(study, g["level"].unique().tolist())
        fig, axes = plt.subplots(1, 3, figsize=(13, 3.6))
        panels = [("psnr", "PSNR vs expected (dB)", "psnr_ci"), ("success", "Success rate (SSIM ≥ 0.90)", None),
                  ("cx", "CNOT count (log)", None)]
        if study in ("interpolation", "normalization", "image"):
            panels[1] = ("e2e_psnr", "End-to-end PSNR vs source (dB)", None)
        for ax, (col, title, err) in zip(axes, panels):
            for enc, ge in g.groupby("encoding"):
                ge = ge.set_index("level").reindex([o for o in order if o in set(ge["level"])])
                x = np.arange(len(ge))
                ax.errorbar(x, ge[col], yerr=ge[err] if err else None, marker="o", capsize=3,
                            color=ENC_COLORS.get(enc), label=ENC_LABELS.get(enc, enc), lw=1.8)
                ax.set_xticks(x, [str(i) for i in ge.index], rotation=30 if len(ge) > 4 else 0)
            ax.set_title(title, fontsize=10)
            ax.set_xlabel(FACTOR_LABELS.get(st.factor, st.factor))
            if col == "cx":
                ax.set_yscale("log")
        axes[0].legend(frameon=False, fontsize=8)
        fig.suptitle(f"{FACTOR_LABELS.get(st.factor, st.factor)} — {st.question}", fontsize=11, x=0.01, ha="left")
        name = f"ofat_{study}.png"
        _save(fig, outdir / name)
        files.append(name)
    return files


def plot_factorial(effects: pd.DataFrame, outdir: Path) -> list[str]:
    files = []
    titles = {"psnr": "Quality (PSNR)", "log_cx": "Efficiency (log CNOTs)", "psnr_sd": "Reliability (PSNR std)",
              "log_time": "Runtime (log s)"}
    for enc, g in effects.groupby("encoding"):
        fig, axes = plt.subplots(1, 4, figsize=(15, 4.2), sharey=False)
        for ax, (resp, title) in zip(axes, titles.items()):
            m = g[(g.response == resp) & (g.order < 3)].sort_values("contribution", ascending=False).head(8)[::-1]
            colors = ["#94a3b8" if o == 2 else ENC_COLORS[enc] for o in m["order"]]
            ax.barh([FACTOR_LABELS.get(t, t) for t in m["term"]], m["contribution"], color=colors)
            for y, (c, p) in enumerate(zip(m["contribution"], m["p_value"])):
                ax.text(c, y, f" {c:.1f}%{'*' if p < 0.05 else ''}", va="center", fontsize=8)
            ax.set_title(title, fontsize=10)
            ax.set_xlabel("% of variance explained")
            ax.grid(axis="y", alpha=0)
        fig.suptitle(f"{ENC_LABELS[enc]} — 2^7 factorial: what drives each performance dimension "
                     "(grey = interaction, * p < 0.05)", fontsize=11, x=0.01, ha="left")
        name = f"factorial_pareto_{enc}.png"
        _save(fig, outdir / name)
        files.append(name)
    return files


def plot_interactions(fact: pd.DataFrame, outdir: Path) -> list[str]:
    pairs = [("noise", "structure"), ("noise", "shots"), ("noise", "operations")]
    fig, axes = plt.subplots(2, 3, figsize=(13, 6.5))
    for r, enc in enumerate(FACTORIAL_FACTORS):
        d = fact[fact.encoding == enc]
        for c, (a, b) in enumerate(pairs):
            ax = axes[r, c]
            m = d.groupby([a, b])["psnr"].mean().unstack(b)
            for col in m.columns:
                ax.plot([str(x) for x in m.index], m[col], marker="o", label=f"{FACTOR_LABELS[b]} = {col}")
            ax.set_title(f"{ENC_LABELS[enc]}: {FACTOR_LABELS[a]} × {FACTOR_LABELS[b]}", fontsize=10)
            ax.set_xlabel(FACTOR_LABELS[a])
            ax.set_ylabel("mean PSNR (dB)")
            ax.legend(frameon=False, fontsize=8)
    name = "factorial_interactions.png"
    _save(fig, outdir / name)
    return [name]


def plot_influence_heatmap(influence: pd.DataFrame, outdir: Path) -> list[str]:
    cols = {"quality_eta2": "Quality", "e2e_eta2": "End-to-end", "efficiency_eta2": "Efficiency",
            "time_eta2": "Runtime", "reliability_eta2": "Reliability"}
    files = []
    for enc in ("frqi", "neqr"):
        d = influence[influence.encoding == enc].set_index("factor")[list(cols)].rename(columns=cols)
        d.index = [FACTOR_LABELS.get(i, i) for i in d.index]
        fig, ax = plt.subplots(figsize=(6.4, 0.42 * len(d) + 1.2))
        im = ax.imshow(d.to_numpy(), cmap="Blues", vmin=0, vmax=1, aspect="auto")
        ax.set_xticks(range(len(cols)), d.columns)
        ax.set_yticks(range(len(d)), d.index)
        for i in range(d.shape[0]):
            for j in range(d.shape[1]):
                v = d.iat[i, j]
                ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=8,
                        color="white" if v > 0.6 else "#0f172a")
        ax.grid(False)
        ax.set_title(f"{ENC_LABELS[enc]} — OFAT influence (η², share of variance)", fontsize=10)
        fig.colorbar(im, ax=ax, fraction=0.04)
        name = f"influence_heatmap_{enc}.png"
        _save(fig, outdir / name)
        files.append(name)
    return files


def plot_edges(edges: pd.DataFrame, outdir: Path) -> list[str]:
    fig, axes = plt.subplots(1, 4, figsize=(15, 3.5))
    for ax, sweep in zip(axes, ["shots", "size", "noise", "threshold"]):
        g = edges[edges.factor == sweep].copy()
        g["level"] = g["level"].astype(str)
        order = ["exact" if v is None else str(v) for v in EDGE_SWEEPS[sweep]]
        m = g.groupby("level")[["edge_f1", "sobel_f1"]].mean().reindex(order)
        x = np.arange(len(m))
        ax.plot(x, m["edge_f1"], marker="o", label="QHED vs exact differences")
        ax.plot(x, m["sobel_f1"], marker="s", ls="--", label="QHED vs Sobel")
        ax.set_xticks(x, m.index, rotation=30)
        ax.set_ylim(0, 1.05)
        ax.set_title(f"Edge F1 vs {sweep}", fontsize=10)
    axes[0].legend(frameon=False, fontsize=8)
    name = "edge_detection.png"
    _save(fig, outdir / name)
    return [name]


# ============================================================ orchestration

def _records(df: pd.DataFrame) -> list[dict]:
    return json.loads(df.replace([np.inf, -np.inf], np.nan).to_json(orient="records"))


def analyse(results_dir: Path) -> dict:
    results_dir = Path(results_dir)
    fig_dir = results_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    summary: dict = {"figures": []}

    ofat_path, fact_path, edge_path = (results_dir / f for f in ("ofat.csv", "factorial.csv", "edges.csv"))
    if ofat_path.exists():
        ofat = pd.read_csv(ofat_path)
        osum = summarize_ofat(ofat)
        infl = ofat_influence(ofat)
        osum.to_csv(results_dir / "ofat_summary.csv", index=False)
        infl.to_csv(results_dir / "ofat_influence.csv", index=False)
        summary["ofat"] = _records(osum)
        summary["influence"] = _records(infl)
        summary["studies"] = [{"name": s.name, "factor": s.factor, "label": FACTOR_LABELS[s.factor],
                               "question": s.question} for s in OFAT_STUDIES]
        summary["figures"] += plot_ofat(osum, fig_dir) + plot_influence_heatmap(infl, fig_dir)
    if fact_path.exists():
        fact = pd.read_csv(fact_path)
        effects = pd.concat([factorial_effects(fact, e) for e in FACTORIAL_FACTORS if (fact.encoding == e).any()])
        effects.to_csv(results_dir / "factorial_effects.csv", index=False)
        summary["factorial"] = _records(effects)
        summary["rankings"] = rankings(effects)
        summary["figures"] += plot_factorial(effects, fig_dir) + plot_interactions(fact, fig_dir)
    if edge_path.exists():
        edges = pd.read_csv(edge_path)
        g = edges.copy()
        g["level"] = g["level"].astype(str)
        summary["edges"] = _records(g.groupby(["factor", "level"]).mean(numeric_only=True).reset_index())
        summary["figures"] += plot_edges(edges, fig_dir)

    (results_dir / "summary.json").write_text(json.dumps(summary, indent=1, default=float))
    return summary
