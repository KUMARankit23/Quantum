"""Notebook visualisations: the dashboard's interactive and animated views, inside Jupyter.

Animations are matplotlib ``FuncAnimation`` objects returned as embedded HTML (they keep playing in
the saved .ipynb). 3-D and dropdown figures are Plotly (rotatable, hoverable, also saved). The live
control panel uses ipywidgets and needs a running kernel.

    from qipbench import viz
    viz.setup()
    r = viz.run(encoding="frqi", size=8)
    viz.pipeline_strip(r)
    viz.shot_replay(r)          # wavefunction collapse, shot by shot
    viz.pixel_bloch(r)          # every pixel's qubit on a rotatable Bloch sphere
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation
from matplotlib.patches import Rectangle

from . import edge, images, metrics
from .analysis import _level_order
from .encoders import EncodedImage, get_encoder
from .pipeline import PipelineConfig, PipelineResult, run as run_pipeline

ROOT = Path(__file__).resolve().parent.parent
ENC_COLORS = {"frqi": "#2a78d6", "neqr": "#eb6834", "amplitude": "#1baf7a"}
ENC_LABELS = {"frqi": "FRQI", "neqr": "NEQR", "amplitude": "Amplitude (QPIE)"}
STATE_COLOR = "#eb6834"


def setup(embed_limit_mb: int = 60) -> None:
    """Notebook styling and embedding defaults."""
    import plotly.io as pio
    plt.rcParams.update({
        "figure.dpi": 100, "font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
        "animation.embed_limit": embed_limit_mb, "animation.html": "jshtml",
        "animation.frame_format": "jpeg", "savefig.dpi": 72,      # keeps embedded animations small
    })
    import sys
    if "google.colab" in sys.modules:      # Colab needs its own renderer and the custom widget manager
        from google.colab import output
        output.enable_custom_widget_manager()
        pio.renderers.default = "colab"
    else:
        pio.renderers.default = "notebook"     # embeds plotly.js once, so figures work offline in the saved file


def _html(anim: animation.FuncAnimation):
    from IPython.display import HTML
    html = anim.to_jshtml(default_mode="once")
    plt.close(anim._fig)
    return HTML(html)


def run(**kw) -> PipelineResult:
    """Shorthand for ``pipeline.run(PipelineConfig(**kw))``."""
    return run_pipeline(PipelineConfig(**kw))


def _encoded_stub(r: PipelineResult) -> EncodedImage:
    L = r.layout
    n, q = L["position"], L["color"]
    return EncodedImage(None, list(range(n)), list(range(n, n + q)),
                        list(range(n + q, n + q + L["ancilla"])), {"norm": L.get("norm")})


def _gray(ax, img, title=None):
    ax.imshow(img, cmap="gray", vmin=0, vmax=1, interpolation="nearest")
    ax.set_xticks([]), ax.set_yticks([])
    if title:
        ax.set_title(title, fontsize=10)


# =========================================================================== static views

def pipeline_strip(r: PipelineResult):
    """Source -> preprocessed -> expected -> reconstruction -> |error| with headline metrics."""
    err = np.abs(r.expected - r.reconstructed)
    fig, ax = plt.subplots(1, 5, figsize=(15, 3.4))
    _gray(ax[0], r.source, "source")
    _gray(ax[1], r.preprocessed.quantized, f"loaded {r.config.size}×{r.config.size}, {r.config.bit_depth}-bit")
    _gray(ax[2], r.expected, f"expected ({r.config.operations} inversions)")
    _gray(ax[3], r.reconstructed, f"{ENC_LABELS[r.config.encoding]} reconstruction")
    im = ax[4].imshow(err, cmap="magma", vmin=0, interpolation="nearest")
    ax[4].set_xticks([]), ax[4].set_yticks([]), ax[4].set_title("|error|", fontsize=10)
    fig.colorbar(im, ax=ax[4], fraction=.046)
    m = r.metrics
    fig.suptitle(f"PSNR {m['psnr']:.1f} dB · SSIM {m['ssim']:.3f} · {m['qubits']} qubits · {m['cx']} CNOTs · "
                 f"depth {m['depth']} · shots {r.config.shots or 'exact'} · noise p={r.config.noise:g}",
                 x=.01, ha="left", fontsize=11, fontweight="bold")
    fig.tight_layout()
    plt.show()


def draw_circuit(qc, fold: int = 30, scale: float = .7):
    """Qiskit matplotlib drawing of the logical circuit."""
    fig = qc.draw("mpl", fold=fold, scale=scale, style="iqp")
    plt.show()
    return fig


def metrics_table(results: dict[str, PipelineResult]):
    import pandas as pd
    cols = ["qubits", "cx", "depth", "psnr", "ssim", "level_accuracy", "fidelity", "coverage", "total_s"]
    return pd.DataFrame({k: {c: v.metrics[c] for c in cols} for k, v in results.items()}).T.round(4)


def structure_comparison(image: str = "camera", size: int = 4, noise: float = 1e-3):
    """Same quantum state, two decompositions: cost and noisy quality side by side."""
    rows = {}
    for enc in ("frqi", "neqr"):
        for st in ("baseline", "optimized"):
            rows[(enc, st)] = run(encoding=enc, image=image, size=size, bit_depth=4, structure=st, noise=noise).metrics
    fig, ax = plt.subplots(1, 3, figsize=(14, 3.6))
    labels = [f"{ENC_LABELS[e]}\n{s}" for e, s in rows]
    colors = [ENC_COLORS[e] for e, _ in rows]
    for a, key, title in zip(ax, ["cx", "depth", "psnr"], ["CNOT count", "Transpiled depth", f"PSNR under p={noise:g} (dB)"]):
        vals = [rows[k][key] for k in rows]
        bars = a.bar(labels, vals, color=colors, alpha=.9)
        for b, s in zip(bars, [s for _, s in rows]):
            b.set_hatch("//" if s == "baseline" else "")
        a.bar_label(bars, fmt="%.0f" if key != "psnr" else "%.1f", fontsize=9)
        a.set_title(title, fontsize=10)
    fig.suptitle("Circuit structure: identical states, very different engineering (hatched = baseline)",
                 x=.01, ha="left", fontweight="bold")
    fig.tight_layout()
    plt.show()


# =========================================================================== Bloch sphere (Plotly)

def _sphere_traces(go):
    u, v = np.mgrid[0:2 * np.pi:40j, 0:np.pi:20j]
    traces = [go.Surface(x=np.cos(u) * np.sin(v), y=np.sin(u) * np.sin(v), z=np.cos(v), opacity=.12,
                         showscale=False, colorscale=[[0, "#2a78d6"], [1, "#2a78d6"]], hoverinfo="skip")]
    t = np.linspace(0, 2 * np.pi, 100)
    for x, y, z in [(np.cos(t), np.sin(t), 0 * t), (np.cos(t), 0 * t, np.sin(t)), (0 * t, np.cos(t), np.sin(t))]:
        traces.append(go.Scatter3d(x=x, y=y, z=z, mode="lines", line=dict(color="#94a3b8", width=2), hoverinfo="skip"))
    for (x, y, z), lbl in [((0, 0, 1.25), "|0⟩"), ((0, 0, -1.25), "|1⟩"), ((1.25, 0, 0), "|+⟩"), ((0, 1.25, 0), "|+i⟩")]:
        traces.append(go.Scatter3d(x=[0, x * .95], y=[0, y * .95], z=[0, z * .95], mode="lines+text", text=["", lbl],
                                   line=dict(color="#64748b", width=3), textfont=dict(size=14), hoverinfo="skip"))
    return traces


def _vector(theta, phi):
    return np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)


def bloch(theta: float, phi: float = 0.0, title: str = "Qubit state"):
    """A single state on a rotatable 3-D Bloch sphere."""
    import plotly.graph_objects as go
    x, y, z = _vector(theta, phi)
    fig = go.Figure(_sphere_traces(go) + [
        go.Scatter3d(x=[0, x], y=[0, y], z=[0, z], mode="lines+markers", line=dict(color=STATE_COLOR, width=8),
                     marker=dict(size=[0, 7], color=STATE_COLOR), name="state")])
    fig.update_layout(title=title, showlegend=False, height=460, margin=dict(l=0, r=0, t=40, b=0),
                      scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, aspectmode="cube"))
    return fig


def pixel_bloch(r: PipelineResult, max_pixels: int = 64):
    """Slider over pixels: the loaded image with the selected pixel, and its FRQI colour qubit on the Bloch sphere.

    FRQI stores pixel i as cos θᵢ|0⟩ + sin θᵢ|1⟩ with θᵢ = (π/2)·Iᵢ, i.e. Bloch polar angle 2θᵢ.
    """
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    img = r.preprocessed.quantized
    s = img.shape[0]
    n_pix = min(s * s, max_pixels)
    fig = make_subplots(rows=1, cols=2, column_widths=[.42, .58], specs=[[{"type": "xy"}, {"type": "scene"}]],
                        subplot_titles=("loaded image", "colour qubit of the selected pixel"))
    fig.add_trace(go.Heatmap(z=img[::-1], colorscale="gray", zmin=0, zmax=1, showscale=False,
                             hovertemplate="row %{customdata[0]}, col %{customdata[1]}<br>I = %{z:.3f}<extra></extra>",
                             customdata=np.dstack(np.meshgrid(np.arange(s), np.arange(s), indexing="ij"))[::-1]), 1, 1)
    for t in _sphere_traces(go):
        fig.add_trace(t, 1, 2)
    base = len(fig.data)
    fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, 1], mode="lines+markers",
                               line=dict(color=STATE_COLOR, width=9), marker=dict(size=[0, 8], color=STATE_COLOR)), 1, 2)
    fig.add_trace(go.Scatter(x=[0], y=[s - 1], mode="markers", marker=dict(symbol="square-open", size=26,
                             color=STATE_COLOR, line=dict(width=3)), hoverinfo="skip"), 1, 1)
    steps = []
    for i in range(n_pix):
        row, col = divmod(i, s)
        th = np.pi / 2 * img[row, col]
        x, y, z = _vector(2 * th, 0)
        label = (f"pixel ({row},{col}) · I={img[row, col]:.3f} · θ={th:.3f} → "
                 f"{np.cos(th):.3f}|0⟩ + {np.sin(th):.3f}|1⟩")
        steps.append(dict(method="update", label=str(i), args=[
            {"x": [[0, x], [col]], "y": [[0, y], [s - 1 - row]], "z": [[0, z], None]}, {"title.text": label}, [base, base + 1]]))
    fig.update_layout(sliders=[dict(active=0, steps=steps, currentvalue=dict(prefix="pixel index "), pad=dict(t=30))],
                      title=dict(text=steps[0]["args"][1]["title.text"], font=dict(size=13)), showlegend=False,
                      width=920, height=520, margin=dict(t=80, b=20, l=20, r=20), plot_bgcolor="rgba(0,0,0,0)",
                      scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, aspectmode="cube"))
    fig.update_xaxes(visible=False, constrain="domain", row=1, col=1)
    fig.update_yaxes(visible=False, scaleanchor="x", constrain="domain", row=1, col=1)
    return fig


# =========================================================================== matplotlib Bloch (for animations)

def _mpl_bloch(ax):
    u, v = np.mgrid[0:2 * np.pi:30j, 0:np.pi:15j]
    ax.plot_wireframe(np.cos(u) * np.sin(v), np.sin(u) * np.sin(v), np.cos(v), color="#cbd5e1", lw=.4)
    t = np.linspace(0, 2 * np.pi, 100)
    ax.plot(np.cos(t), np.sin(t), 0, color="#94a3b8", lw=1)
    ax.plot(np.cos(t), 0 * t, np.sin(t), color="#94a3b8", lw=1, ls="--")
    for (x, y, z), lbl in [((0, 0, 1.3), "|0⟩"), ((0, 0, -1.35), "|1⟩"), ((1.35, 0, 0), "|+⟩"), ((0, 1.35, 0), "|+i⟩")]:
        ax.text(x, y, z, lbl, ha="center", fontsize=11)
    ax.set_box_aspect((1, 1, 1))
    ax.set_xlim(-1, 1), ax.set_ylim(-1, 1), ax.set_zlim(-1, 1)
    ax.axis("off")
    ax.view_init(elev=18, azim=35)


def bloch_precession(frames: int = 60):
    """Larmor-style precession: phase φ advances while the populations stay fixed."""
    fig = plt.figure(figsize=(4.6, 4.6))
    ax = fig.add_subplot(projection="3d")
    _mpl_bloch(ax)
    line, = ax.plot([], [], [], color=STATE_COLOR, lw=3)
    trail, = ax.plot([], [], [], color=STATE_COLOR, lw=1, alpha=.4)
    title = ax.set_title("")
    hist = []

    def step(k):
        phi = 2 * np.pi * k / frames
        theta = 1.0 + .3 * np.sin(4 * np.pi * k / frames)
        x, y, z = _vector(theta, phi)
        hist.append((x, y, z))
        line.set_data_3d([0, x], [0, y], [0, z])
        h = np.array(hist[-40:])
        trail.set_data_3d(h[:, 0], h[:, 1], h[:, 2])
        title.set_text(f"cos(θ/2)|0⟩ + e^(iφ) sin(θ/2)|1⟩   θ={theta:.2f}  φ={phi:.2f}")
        return line, trail
    return _html(animation.FuncAnimation(fig, step, frames=frames, interval=50))


def pixel_scan(r: PipelineResult, interval: int = 450):
    """Animated scan over every pixel: highlighted pixel and its FRQI colour qubit on the Bloch sphere."""
    img = r.preprocessed.quantized
    s = img.shape[0]
    fig = plt.figure(figsize=(9, 4.2))
    ax_img = fig.add_subplot(1, 2, 1)
    ax_b = fig.add_subplot(1, 2, 2, projection="3d")
    _gray(ax_img, img, "loaded image")
    box = Rectangle((-.5, -.5), 1, 1, fill=False, ec=STATE_COLOR, lw=3)
    ax_img.add_patch(box)
    _mpl_bloch(ax_b)
    vec, = ax_b.plot([], [], [], color=STATE_COLOR, lw=3.5)
    tip, = ax_b.plot([], [], [], "o", color=STATE_COLOR, ms=7)
    txt = fig.text(.5, .02, "", ha="center", family="monospace", fontsize=10)

    def step(i):
        row, col = divmod(i, s)
        th = np.pi / 2 * img[row, col]
        x, y, z = _vector(2 * th, 0)
        box.set_xy((col - .5, row - .5))
        vec.set_data_3d([0, x], [0, y], [0, z])
        tip.set_data_3d([x], [y], [z])
        pos = format(i, f"0{int(np.log2(s * s))}b")
        txt.set_text(f"pixel ({row},{col})  I={img[row, col]:.3f}  θ={th:.3f}   "
                     f"|ψᵢ⟩ = {np.cos(th):.3f}|0⟩ + {np.sin(th):.3f}|1⟩  ⊗ |{pos}⟩")
        return box, vec, tip, txt
    return _html(animation.FuncAnimation(fig, step, frames=s * s, interval=interval))


# =========================================================================== measurement replay

def _replay_checkpoints(r: PipelineResult, frames: int, seed: int):
    rng = np.random.default_rng(seed)
    dist = r.distribution
    if r.config.shots is None:                         # exact: sample shots from |ψ|²
        total = 4096
        outcomes = rng.choice(dist.size, size=total, p=dist / dist.sum())
    else:                                              # the real measured shots, in random order
        outcomes = np.repeat(np.arange(dist.size), np.rint(dist).astype(int))
        rng.shuffle(outcomes)
        total = outcomes.size
    marks = np.unique(np.geomspace(8, total, frames).astype(int))
    return outcomes, marks, total


def shot_replay(r: PipelineResult, frames: int = 32, seed: int = 0):
    """Wavefunction collapse, shot by shot: the image is decoded from the first k shots, k growing.

    Uses the real measured outcomes (shuffled) and the same decoder as the pipeline.
    """
    enc = get_encoder(r.config.encoding)
    stub = _encoded_stub(r)
    shape = r.expected.shape
    outcomes, marks, total = _replay_checkpoints(r, frames, seed)
    top = np.argsort(r.distribution)[::-1][:24]
    estimator = enc.estimators[0] if r.config.estimator == "auto" else r.config.estimator

    fig, ax = plt.subplots(1, 4, figsize=(16, 3.8), gridspec_kw=dict(width_ratios=[1, 1, 1.6, 1.3]))
    _gray(ax[0], r.expected, "expected")
    im = ax[1].imshow(np.zeros(shape), cmap="gray", vmin=0, vmax=1, interpolation="nearest")
    ax[1].set_xticks([]), ax[1].set_yticks([])
    mask = ax[1].imshow(np.zeros((*shape, 4)), interpolation="nearest")
    t1 = ax[1].set_title("")
    bars = ax[2].bar(range(len(top)), np.zeros(len(top)), color=ENC_COLORS[r.config.encoding])
    ax[2].set_ylim(0, r.distribution[top].max() / r.distribution.sum() * 1.15)
    nbits = r.layout["position"] + r.layout["color"] + r.layout["ancilla"]
    ax[2].set_xticks(range(len(top)), [format(i, f"0{nbits}b") for i in top], rotation=90, fontsize=6, family="monospace")
    ax[2].set_title("measured basis states |colour⟩|position⟩ (relative frequency)", fontsize=10)
    ax[3].set_xscale("log"), ax[3].set_xlim(marks[0], total), ax[3].set_ylim(0, 62)
    ax[3].set_xlabel("shots"), ax[3].set_ylabel("PSNR (dB)"), ax[3].grid(alpha=.3)
    curve, = ax[3].plot([], [], color=ENC_COLORS[r.config.encoding], lw=2, marker="o", ms=3)
    ax[3].set_title("quality vs shots", fontsize=10)
    xs, ys = [], []
    fig.tight_layout()

    def step(k):
        n = marks[k]
        counts = np.bincount(outcomes[:n], minlength=r.distribution.size).astype(float)
        rec, cov = enc.decode(counts, shape, stub, estimator, "zero")
        im.set_data(rec)
        pos_seen = counts.reshape(-1, shape[0] * shape[1]).sum(0).reshape(shape) > 0
        overlay = np.zeros((*shape, 4))
        overlay[~pos_seen] = (0.16, 0.47, 0.84, .55)          # unobserved = still in superposition
        mask.set_data(overlay)
        t1.set_text(f"collapsed after {n:,} / {total:,} shots · coverage {cov:.0%}")
        freq = counts[top] / n
        for b, h in zip(bars, freq):
            b.set_height(h)
        ax[2].set_ylim(0, max(freq.max(), r.distribution[top].max() / r.distribution.sum()) * 1.15)
        xs.append(n), ys.append(metrics.psnr(r.expected, rec))
        curve.set_data(xs, ys)
        return [im, mask, curve, *bars]
    return _html(animation.FuncAnimation(fig, step, frames=len(marks), interval=120))


# =========================================================================== factor sweeps as animations

def noise_sweep(image: str = "camera", levels=(0, 1e-4, 3e-4, 1e-3, 2e-3, 3e-3, 5e-3, 7e-3, 1e-2, 1.5e-2),
                size: int = 4, bit_depth: int = 4, seed: int = 0):
    """FRQI degrades gracefully, NEQR is perfect then collapses: watch both as noise grows."""
    res = {e: [run(encoding=e, image=image, size=size, bit_depth=bit_depth, noise=p, seed=seed) for p in levels]
           for e in ("frqi", "neqr")}
    fig, ax = plt.subplots(1, 4, figsize=(15, 3.8), gridspec_kw=dict(width_ratios=[1, 1, 1, 1.8]))
    _gray(ax[0], res["frqi"][0].expected, "expected")
    ims = {e: ax[i + 1].imshow(np.zeros((size, size)), cmap="gray", vmin=0, vmax=1, interpolation="nearest")
           for i, e in enumerate(("frqi", "neqr"))}
    titles = {e: ax[i + 1].set_title("") for i, e in enumerate(("frqi", "neqr"))}
    for a in ax[1:3]:
        a.set_xticks([]), a.set_yticks([])
    lines = {e: ax[3].plot([], [], marker="o", color=ENC_COLORS[e], lw=2, label=ENC_LABELS[e])[0] for e in res}
    ax[3].set_xscale("symlog", linthresh=1e-4), ax[3].set_xlim(0, levels[-1] * 1.1), ax[3].set_ylim(0, 63)
    ax[3].set_xlabel("noise p"), ax[3].set_ylabel("PSNR (dB)"), ax[3].legend(frameon=False), ax[3].grid(alpha=.3)
    marker = ax[3].axvline(0, color="#64748b", ls=":")
    fig.suptitle("Noise sweep: graceful (FRQI) vs threshold (NEQR) degradation", x=.01, ha="left", fontweight="bold")
    fig.tight_layout()

    def step(k):
        for e in res:
            rr = res[e][k]
            ims[e].set_data(rr.reconstructed)
            titles[e].set_text(f"{ENC_LABELS[e]} · {rr.metrics['psnr']:.1f} dB")
            lines[e].set_data(levels[:k + 1], [x.metrics["psnr"] for x in res[e][:k + 1]])
        marker.set_xdata([levels[k]])
        return list(ims.values()) + list(lines.values())
    return _html(animation.FuncAnimation(fig, step, frames=len(levels), interval=700))


def factor_sweep(factor: str, levels, encoding: str = "frqi", image: str = "camera", **base):
    """Generic animation: reconstruction and PSNR as any single PipelineConfig factor changes."""
    cfg = {"encoding": encoding, "image": image, **base}
    res = [run(**{**cfg, factor: lv}) for lv in levels]
    fig, ax = plt.subplots(1, 3, figsize=(12, 3.8), gridspec_kw=dict(width_ratios=[1, 1, 1.6]))
    im0 = ax[0].imshow(res[0].expected, cmap="gray", vmin=0, vmax=1, interpolation="nearest")
    im1 = ax[1].imshow(res[0].reconstructed, cmap="gray", vmin=0, vmax=1, interpolation="nearest")
    for a in ax[:2]:
        a.set_xticks([]), a.set_yticks([])
    t0, t1 = ax[0].set_title("expected"), ax[1].set_title("")
    x = np.arange(len(levels))
    ax[2].set_xticks(x, [str(lv) for lv in levels]), ax[2].set_xlim(-.3, len(levels) - .7), ax[2].set_ylim(0, 63)
    ax[2].set_xlabel(factor), ax[2].set_ylabel("PSNR (dB)"), ax[2].grid(alpha=.3)
    ax2b = ax[2].twinx()
    ax2b.set_ylabel("CNOTs", color="#64748b")
    ax2b.set_ylim(0, max(r.metrics["cx"] for r in res) * 1.15)
    l1, = ax[2].plot([], [], "o-", color=ENC_COLORS[encoding], lw=2, label="PSNR")
    l2, = ax2b.plot([], [], "s--", color="#64748b", label="CNOTs")
    fig.suptitle(f"{ENC_LABELS[encoding]}: effect of {factor}", x=.01, ha="left", fontweight="bold")
    fig.tight_layout()

    def step(k):
        r = res[k]
        im0.set_data(r.expected), im1.set_data(r.reconstructed)
        t0.set_text(f"expected ({r.expected.shape[0]}×{r.expected.shape[0]})")
        t1.set_text(f"{factor}={levels[k]} · {r.metrics['psnr']:.1f} dB · {r.metrics['qubits']} qubits")
        l1.set_data(x[:k + 1], [q.metrics["psnr"] for q in res[:k + 1]])
        l2.set_data(x[:k + 1], [q.metrics["cx"] for q in res[:k + 1]])
        return im0, im1, l1, l2
    return _html(animation.FuncAnimation(fig, step, frames=len(levels), interval=800))


# =========================================================================== edge detection

def qhed_animation(image: str = "blocks", size: int = 16, threshold: float = .2,
                   shots=(128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536, None)):
    """Edges emerging from measurement statistics, compared with the exact classical answer."""
    img = images.preprocess(images.load_standard(image), size).quantized
    res = [edge.detect(img, threshold, s, seed=1) for s in shots]
    fig, ax = plt.subplots(1, 5, figsize=(16, 3.6), gridspec_kw=dict(width_ratios=[1, 1, 1, 1, 1.6]))
    _gray(ax[0], img, "input")
    g = ax[1].imshow(np.zeros_like(img), cmap="magma", vmin=0, vmax=res[-1].classical_magnitude.max(), interpolation="nearest")
    e = ax[2].imshow(np.zeros_like(img), cmap="gray", vmin=0, vmax=1, interpolation="nearest")
    _gray(ax[3], res[-1].classical_edges, "exact classical edges")
    for a in ax[1:3]:
        a.set_xticks([]), a.set_yticks([])
    tg, te = ax[1].set_title("quantum |∇|"), ax[2].set_title("")
    x = np.arange(len(shots))
    ax[4].set_xticks(x, [str(s or "exact") for s in shots], rotation=45, fontsize=8)
    ax[4].set_xlim(-.3, len(shots) - .7), ax[4].set_ylim(0, 1.05), ax[4].grid(alpha=.3)
    ax[4].set_ylabel("edge F1"), ax[4].set_xlabel("shots per scan")
    f1, = ax[4].plot([], [], "o-", color=ENC_COLORS["amplitude"], lw=2, label="vs exact differences")
    f2, = ax[4].plot([], [], "s--", color="#64748b", lw=1.5, label="vs Sobel")
    ax[4].legend(frameon=False, fontsize=8)
    fig.suptitle(f"QHED on {size}×{size} '{image}': {res[0].metrics['qubits']} qubits, "
                 f"{res[0].metrics['cx']} CNOTs per scan", x=.01, ha="left", fontweight="bold")
    fig.tight_layout()

    def step(k):
        r = res[k]
        g.set_data(r.magnitude), e.set_data(r.edges.astype(float))
        te.set_text(f"quantum edges · {shots[k] or 'exact'} shots")
        f1.set_data(x[:k + 1], [q.metrics["edge_f1"] for q in res[:k + 1]])
        f2.set_data(x[:k + 1], [q.metrics["sobel_f1"] for q in res[:k + 1]])
        return g, e, f1, f2
    return _html(animation.FuncAnimation(fig, step, frames=len(shots), interval=700))


# =========================================================================== research results (Plotly)

def load_summary(results_dir: Path | str = ROOT / "results") -> dict:
    return json.loads((Path(results_dir) / "summary.json").read_text())


def factor_ranking(summary: dict):
    """Interactive bar chart: dropdown over encoding x dimension, hover for effect size and p-value."""
    import plotly.graph_objects as go
    rk = summary["rankings"]
    dims = ["quality", "efficiency", "reliability", "runtime"]
    fig = go.Figure()
    buttons, k = [], 0
    for enc in rk:
        for dim in dims:
            rows = rk[enc][dim][::-1]
            fig.add_trace(go.Bar(
                x=[r["contribution"] for r in rows], y=[r["label"] for r in rows], orientation="h",
                marker_color=[ENC_COLORS[enc] if r["p_value"] < .05 else "#cbd5e1" for r in rows],
                customdata=[[r["effect"], r["p_value"]] for r in rows], visible=(k == 0),
                hovertemplate="%{y}: %{x:.1f}% of variance<br>effect %{customdata[0]:.3f}, p=%{customdata[1]:.1e}<extra></extra>"))
            vis = [False] * (len(rk) * len(dims))
            vis[k] = True
            split = rk[enc][dim + "_split"]
            buttons.append(dict(label=f"{ENC_LABELS[enc]} · {dim}", method="update", args=[
                {"visible": vis}, {"title.text": f"{ENC_LABELS[enc]} {dim}: main {split['main']}% · "
                                                 f"2-way {split['two_way']}% · higher-order {split['higher_order']}%"}]))
            k += 1
    fig.update_layout(updatemenus=[dict(buttons=buttons, x=0, y=1.18, xanchor="left")],
                      title=buttons[0]["args"][1]["title.text"], height=430, margin=dict(t=110, l=10),
                      xaxis_title="% of variance explained (grey = not significant)")
    return fig


def ofat_explorer(summary: dict, metric: str = "psnr"):
    """Dropdown over all OFAT studies; one line per encoding with 95% CI on PSNR."""
    import plotly.graph_objects as go
    import pandas as pd
    df = pd.DataFrame(summary["ofat"])
    studies = summary["studies"]
    fig = go.Figure()
    buttons, idx = [], 0
    for si, st in enumerate(studies):
        g = df[df.study == st["name"]].copy()
        order = _level_order(st["name"], g["level"].astype(str).unique().tolist())
        g["_rank"] = g["level"].astype(str).map({lv: i for i, lv in enumerate(order)})
        g = g.sort_values("_rank")
        start = idx
        for enc, ge in g.groupby("encoding"):
            err = dict(type="data", array=ge["psnr_ci"]) if metric == "psnr" else None
            fig.add_trace(go.Scatter(x=ge["level"].astype(str), y=ge[metric], mode="lines+markers", name=ENC_LABELS[enc],
                                     line=dict(color=ENC_COLORS[enc], width=2.5), error_y=err, visible=(si == 0),
                                     hovertemplate=f"{ENC_LABELS[enc]}<br>%{{x}}: %{{y:.3f}}<extra></extra>"))
            idx += 1
        buttons.append((st, start, idx))
    menu = []
    for st, a, b in buttons:
        vis = [a <= i < b for i in range(idx)]
        menu.append(dict(label=st["label"], method="update",
                         args=[{"visible": vis}, {"title.text": f"{st['label']}: {st['question']}", "xaxis.title.text": st["label"]}]))
    first = buttons[0][0]
    fig.update_layout(updatemenus=[dict(buttons=menu, x=0, y=1.2, xanchor="left")], height=460,
                      title=f"{first['label']}: {first['question']}", xaxis_title=first["label"], yaxis_title=metric,
                      margin=dict(t=110), xaxis_type="category", legend=dict(orientation="h", y=-0.2))
    return fig


# =========================================================================== live control panel (ipywidgets)

def lab():
    """Interactive control panel: every pipeline factor, a Run button, live results and replay."""
    import ipywidgets as w
    from IPython.display import clear_output, display

    style = {"description_width": "110px"}
    lay = w.Layout(width="300px")
    ctl = {
        "encoding": w.ToggleButtons(options=[("FRQI", "frqi"), ("NEQR", "neqr"), ("QPIE", "amplitude")], value="frqi"),
        "image": w.Dropdown(options=list(images.STANDARD_IMAGES), value="camera", description="image", style=style, layout=lay),
        "size": w.SelectionSlider(options=[2, 4, 8, 16], value=4, description="size", style=style, layout=lay),
        "bit_depth": w.SelectionSlider(options=[1, 2, 4, 6, 8], value=8, description="bit depth", style=style, layout=lay),
        "interpolation": w.Dropdown(options=list(images.INTERPOLATIONS), value="area", description="interpolation", style=style, layout=lay),
        "normalization": w.Dropdown(options=list(images.NORMALIZATIONS), value="minmax", description="normalisation", style=style, layout=lay),
        "structure": w.ToggleButtons(options=["optimized", "baseline"], value="optimized"),
        "opt_level": w.IntSlider(1, 0, 3, description="transpiler", style=style, layout=lay),
        "operations": w.IntSlider(0, 0, 8, description="inversions", style=style, layout=lay),
        "shots": w.SelectionSlider(options=[("64", 64), ("256", 256), ("1k", 1024), ("4k", 4096), ("16k", 16384), ("exact", None)],
                                   value=4096, description="shots", style=style, layout=lay),
        "noise": w.SelectionSlider(options=[0, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2], value=0, description="noise p", style=style, layout=lay),
    }
    go_btn = w.Button(description="Run quantum pipeline", button_style="primary", icon="play", layout=w.Layout(width="300px"))
    replay = w.Checkbox(value=True, description="animate shot replay")
    out = w.Output()

    def on_run(_):
        cfg = {k: c.value for k, c in ctl.items()}
        with out:
            clear_output(wait=True)
            if cfg["noise"] and cfg["shots"] is None:
                cfg["shots"] = 4096
            if cfg["encoding"] == "amplitude":
                cfg["operations"] = 0
            q = get_encoder(cfg["encoding"]).n_qubits((cfg["size"],) * 2, cfg["bit_depth"], cfg["structure"])
            if q > 18 or (cfg["noise"] and q > 12):
                print(f"{q} qubits is too large for this setting (exact ≤ 18, noisy ≤ 12). Reduce size or bit depth.")
                return
            print("simulating…")
            r = run(**cfg)
            clear_output(wait=True)
            pipeline_strip(r)
            if replay.value:
                display(shot_replay(r, frames=30))
            if r.circuit.num_qubits <= 7 and r.circuit.size() < 60:
                draw_circuit(r.circuit)

    go_btn.on_click(on_run)
    left = w.VBox([w.HTML("<b>1 · Preprocess</b>"), ctl["image"], ctl["size"], ctl["bit_depth"], ctl["interpolation"],
                   ctl["normalization"]])
    mid = w.VBox([w.HTML("<b>2 · Encode & operate</b>"), ctl["encoding"], ctl["structure"], ctl["opt_level"], ctl["operations"]])
    right = w.VBox([w.HTML("<b>3 · Measure</b>"), ctl["shots"], ctl["noise"], replay, go_btn])
    display(w.VBox([w.HBox([left, mid, right]), out]))
    on_run(None)
