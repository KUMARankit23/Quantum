"""Command-line interface.

    python -m qipbench demo                       one pipeline run, printed metrics
    python -m qipbench run [--study all] [--quick] run controlled experiments -> results/*.csv
    python -m qipbench report                     analyse results -> figures, summary.json, REPORT.md
    python -m qipbench serve                      start the web dashboard (http://127.0.0.1:8000)
    python -m qipbench package                    zip the project for Google Colab (dist/qip-bench.zip)
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"


def _demo(args):
    from .pipeline import PipelineConfig, run
    cfg = PipelineConfig(encoding=args.encoding, image=args.image, size=args.size, bit_depth=args.bit_depth,
                         shots=None if args.shots == 0 else args.shots, noise=args.noise,
                         structure=args.structure, operations=args.operations)
    r = run(cfg)
    print(f"\n{cfg}\n")
    for k, v in r.metrics.items():
        print(f"  {k:<16} {v:.4g}" if isinstance(v, float) else f"  {k:<16} {v}")
    if r.circuit.num_qubits <= 7 and r.circuit.size() < 80:
        print(r.circuit.draw("text", fold=120))


def _run(args):
    from . import studies
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    which = {"ofat", "factorial", "edges"} if args.study == "all" else {args.study}
    t0 = time.perf_counter()
    if "ofat" in which:
        print("One-factor-at-a-time sweeps")
        studies.run_ofat(workers=args.workers, quick=args.quick).to_csv(out / "ofat.csv", index=False)
    if "factorial" in which:
        print("2^7 factorial screening")
        studies.run_factorial(workers=args.workers, quick=args.quick).to_csv(out / "factorial.csv", index=False)
    if "edges" in which:
        print("Quantum edge detection (QHED)")
        studies.run_edges(workers=args.workers, quick=args.quick).to_csv(out / "edges.csv", index=False)
    print(f"done in {time.perf_counter() - t0:.0f}s -> {out}")
    if not args.no_report:
        _report(args)


def _report(args):
    from .analysis import analyse
    from .report import write_report
    out = Path(getattr(args, "out", RESULTS))
    summary = analyse(out)
    path = write_report(summary, out)
    print(f"report -> {path}")


def _package(args):
    """Zip the project (code, results, notebooks, docs) for upload to Google Colab."""
    import zipfile
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    target = dist / "qip-bench.zip"
    keep = ["qipbench", "web", "tests", "results", "notebooks", "docs",
            "README.md", "requirements.txt", "pyproject.toml", "QIP_Bench_Colab.ipynb"]
    skip = {"__pycache__", ".ipynb_checkpoints", ".pytest_cache"}
    n = 0
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        for item in keep:
            path = ROOT / item
            files = [path] if path.is_file() else [f for f in path.rglob("*") if f.is_file()]
            for f in files:
                if skip.isdisjoint(f.parts):
                    z.write(f, Path("qip-bench") / f.relative_to(ROOT))
                    n += 1
    print(f"{n} files -> {target} ({target.stat().st_size / 2 ** 20:.1f} MB)")


def _serve(args):
    import uvicorn
    print(f"QIP-Bench dashboard on http://{args.host}:{args.port}")
    uvicorn.run("qipbench.server:app", host=args.host, port=args.port, log_level="warning")


def main(argv=None):
    p = argparse.ArgumentParser(prog="qipbench", description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("demo", help="run one pipeline configuration")
    d.add_argument("--encoding", default="frqi", choices=["frqi", "neqr", "amplitude"])
    d.add_argument("--image", default="camera")
    d.add_argument("--size", type=int, default=4)
    d.add_argument("--bit-depth", type=int, default=8)
    d.add_argument("--shots", type=int, default=4096, help="0 = exact probabilities")
    d.add_argument("--noise", type=float, default=0.0)
    d.add_argument("--structure", default="optimized", choices=["baseline", "optimized"])
    d.add_argument("--operations", type=int, default=0)
    d.set_defaults(fn=_demo)

    r = sub.add_parser("run", help="run controlled experiments")
    r.add_argument("--study", default="all", choices=["all", "ofat", "factorial", "edges"])
    r.add_argument("--quick", action="store_true", help="1 image x 1 seed (smoke test, ~1-2 min)")
    r.add_argument("--workers", type=int, default=None)
    r.add_argument("--no-report", action="store_true")
    r.add_argument("--out", default=str(RESULTS), help="results folder (default: results/)")
    r.set_defaults(fn=_run)

    rp = sub.add_parser("report", help="analyse results and write REPORT.md")
    rp.add_argument("--out", default=str(RESULTS), help="results folder (default: results/)")
    rp.set_defaults(fn=_report)

    sub.add_parser("package", help="zip the project for Google Colab -> dist/qip-bench.zip").set_defaults(fn=_package)

    s = sub.add_parser("serve", help="start the web dashboard")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=8000)
    s.set_defaults(fn=_serve)

    args = p.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
