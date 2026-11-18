"""Render docs/VIVA_GUIDE.md to docs/VIVA_GUIDE.pdf (styled HTML printed by headless Chrome or Edge).

    python docs/build_viva_pdf.py
"""
import re
import shutil
import subprocess
import tempfile
from datetime import date
from pathlib import Path

import markdown
from pygments.formatters import HtmlFormatter

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "VIVA_GUIDE.md"
OUT_PDF = ROOT / "docs" / "VIVA_GUIDE.pdf"
HTML = Path(tempfile.gettempdir()) / "qipbench_viva_guide.html"

FORMULAS = {
    r"$$|I\rangle = \frac{1}{\sqrt N}\sum_i (\cos\theta_i|0\rangle + \sin\theta_i|1\rangle)\otimes|i\rangle,\qquad \theta_i=\frac{\pi}{2}I_i$$":
        "|I⟩ = (1/√N) · Σ<sub>i</sub> ( cos θ<sub>i</sub> |0⟩ + sin θ<sub>i</sub> |1⟩ ) ⊗ |i⟩ &nbsp;&nbsp;&nbsp; with &nbsp; θ<sub>i</sub> = (π/2) · I<sub>i</sub>",
    r"$$|I\rangle = \frac{1}{\sqrt N}\sum_i |C_i\rangle\otimes|i\rangle$$":
        "|I⟩ = (1/√N) · Σ<sub>i</sub> |C<sub>i</sub>⟩ ⊗ |i⟩ &nbsp;&nbsp;&nbsp; C<sub>i</sub> = q-bit binary grey level",
    r"$$|I\rangle=\sum_i c_i|i\rangle,\qquad c_i = \frac{I_i}{\lVert I\rVert}$$":
        "|I⟩ = Σ<sub>i</sub> c<sub>i</sub> |i⟩ &nbsp;&nbsp;&nbsp; with &nbsp; c<sub>i</sub> = I<sub>i</sub> / ‖I‖",
}

text = SRC.read_text(encoding="utf-8")
for tex, html in FORMULAS.items():
    assert tex in text, tex[:40]
    text = text.replace(tex, f'<div class="formula">{html}</div>')
assert "$$" not in text

# title, intro and hand-written contents are replaced by the cover + generated contents page
intro_md = text.split("## Contents", 1)[0].split("\n", 2)[2].replace("---", "")
text = "# Part A" + text.split("\n# Part A", 1)[1]
intro = markdown.markdown(intro_md)

# Python-Markdown needs a blank line before a list that follows a paragraph (GitHub does not)
LIST = re.compile(r"^\s*([-*]|\d+\.)\s")
fixed, in_code, prev = [], False, ""
for line in text.split("\n"):
    if line.strip().startswith("```"):
        in_code = not in_code
    if (not in_code and LIST.match(line) and prev.strip() and not LIST.match(prev)
            and not prev.lstrip().startswith(("|", ">"))):
        fixed.append("")
    fixed.append(line)
    prev = line
text = "\n".join(fixed)

md = markdown.Markdown(extensions=["tables", "fenced_code", "codehilite", "toc", "sane_lists"],
                       extension_configs={"codehilite": {"guess_lang": False, "css_class": "hl"},
                                          "toc": {"toc_depth": "1-2"}})
body = md.convert(text)
toc = md.toc

# every "# Part" starts on a new page
body = body.replace("<h1 ", '<h1 class="part" ', ).replace('<h1 class="part" id="qip-bench-complete-viva-guide"',
                                                            '<h1 id="qip-bench-complete-viva-guide"')
def _widen(m):
    plain = re.sub(r"<[^>]+>", "", m.group(0))
    longest = max(len(l) for l in plain.split("\n"))
    if longest <= 96:
        return m.group(0)
    size = max(5.6, min(8.0, 8.6 * 100 / longest))     # shrink so the longest line fits the page
    return m.group(0).replace('<div class="hl">', f'<div class="hl wide" style="font-size:{size:.1f}pt">', 1)


body = re.sub(r'<div class="hl">.*?</div>', _widen, body, flags=re.S)
pyg = HtmlFormatter(style="friendly").get_style_defs(".hl")

css = """
@page { size: A4; margin: 18mm 16mm 18mm 16mm;
  @bottom-center { content: counter(page); } }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: "Segoe UI", Inter, Arial, sans-serif; font-size: 10.4pt; line-height: 1.5; color: #1f2937; margin: 0; }
h1, h2, h3, h4 { color: #0f172a; line-height: 1.25; page-break-after: avoid; break-after: avoid; }
h1 { font-size: 21pt; margin: 0 0 10px; padding-bottom: 6px; border-bottom: 3px solid #2a78d6; }
h1.part { break-before: page; page-break-before: always; }
h2 { font-size: 14.5pt; margin: 22px 0 8px; color: #1d4ed8; border-bottom: 1px solid #dbe3ef; padding-bottom: 3px; }
h3 { font-size: 12pt; margin: 18px 0 6px; color: #0f172a; }
h4 { font-size: 11pt; margin: 14px 0 4px; }
p { margin: 6px 0; }
a { color: #1d4ed8; text-decoration: none; }
strong { color: #0f172a; }
code { font-family: Consolas, "Cascadia Mono", monospace; font-size: 9pt; background: #eef2f7; padding: 1px 4px; border-radius: 3px; }
pre { font-size: 8.6pt; line-height: 1.38; }
.hl { background: #f6f8fb; border: 1px solid #dbe3ef; border-left: 4px solid #2a78d6; border-radius: 6px; padding: 8px 12px;
  margin: 8px 0 10px; break-inside: avoid; page-break-inside: avoid; overflow: hidden; }
.hl pre { margin: 0; white-space: pre-wrap; word-break: break-word; }
.hl.wide pre { white-space: pre; font-size: inherit; line-height: 1.3; }
.hl.wide { break-inside: auto; page-break-inside: auto; }
pre code { background: none; padding: 0; font-size: inherit; }
table { border-collapse: collapse; width: 100%; margin: 8px 0 12px; font-size: 9.2pt; break-inside: auto; }
tr { break-inside: avoid; page-break-inside: avoid; }
th { background: #1d4ed8; color: #fff; text-align: left; padding: 5px 7px; font-weight: 600; }
td { padding: 4px 7px; border-bottom: 1px solid #e5e9f0; vertical-align: top; }
tr:nth-child(even) td { background: #f7f9fc; }
td code { font-size: 8.4pt; }
blockquote { margin: 10px 0; padding: 8px 14px; background: #eef5ff; border-left: 4px solid #2a78d6; border-radius: 4px; color: #1e3a8a; }
blockquote p { margin: 2px 0; }
hr { border: 0; border-top: 1px solid #dbe3ef; margin: 16px 0; }
ul, ol { margin: 4px 0 8px; padding-left: 22px; }
li { margin: 2px 0; }
.formula { font-family: "Cambria Math", Cambria, "Times New Roman", serif; font-size: 13pt; text-align: center;
  background: #f6f8fb; border: 1px solid #dbe3ef; border-radius: 8px; padding: 10px 12px; margin: 10px 0; break-inside: avoid; }
/* cover */
.cover { height: 247mm; display: flex; flex-direction: column; justify-content: center; break-after: page; page-break-after: always; }
.cover .tag { color: #2a78d6; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; font-size: 10pt; }
.cover h1 { border: 0; font-size: 34pt; margin: 8px 0 4px; }
.cover .sub { font-size: 15pt; color: #334155; margin: 0 0 26px; }
.cover .box { border: 1px solid #dbe3ef; border-left: 5px solid #2a78d6; border-radius: 8px; padding: 14px 18px; font-size: 11pt; background: #f6f8fb; }
.cover .box p { margin: 4px 0; }
.cover .orbit { width: 120px; height: 120px; margin-bottom: 24px; }
/* contents */
.toc-page { break-after: page; page-break-after: always; }
.toc-page h2 { border: 0; font-size: 18pt; color: #0f172a; margin-top: 18px; }
.intro p { font-size: 10.5pt; }
.toc ul { list-style: none; padding-left: 0; }
.toc > ul > li > ul > li { margin: 0; }
.toc li a { color: #1f2937; }
.toc > ul > li { margin-top: 10px; }
.toc > ul > li > a { font-weight: 700; color: #1d4ed8; font-size: 11pt; }
.toc ul ul { padding-left: 18px; font-size: 10pt; }
.toc ul ul ul { display: none; }
"""

orbit = """<svg class="orbit" viewBox="0 0 32 32"><circle cx="16" cy="16" r="3.4" fill="#2a78d6"/>
<g fill="none" stroke="#2a78d6" stroke-width="1"><ellipse cx="16" cy="16" rx="13" ry="5"/>
<ellipse cx="16" cy="16" rx="13" ry="5" transform="rotate(60 16 16)"/><ellipse cx="16" cy="16" rx="13" ry="5" transform="rotate(120 16 16)"/></g>
<circle cx="29" cy="16" r="1.4" fill="#eb6834"/></svg>"""

cover = f"""<section class="cover">
{orbit}
<div class="tag">CSE3728 · Quantum Image Processing &amp; Emerging Visual Computing</div>
<h1>QIP-Bench<br>Complete Viva Guide</h1>
<p class="sub">Architecture, every file and function, every test, and the viva questions, explained in simple language</p>
<div class="box">
<p><b>Research question (Problem 9):</b> What really determines the performance of a quantum image-processing system?</p>
<p><b>Project:</b> FRQI · NEQR · QPIE encodings, QHED edge detection, controlled experiments on Qiskit Aer</p>
<p><b>Institution:</b> BML Munjal University · Batch 2023-27 · Academic year 2026-27</p>
<p><b>Generated:</b> {date.today():%d %B %Y}</p>
</div>
</section>"""

toc_page = f'<section class="toc-page"><div class="intro">{intro}</div><h2>Contents</h2>{toc}</section>'
# drop the H1 title from the body (it is on the cover) and its intro paragraph stays
body = re.sub(r'<h1 id="qip-bench-complete-viva-guide">.*?</h1>', "", body, count=1)

HTML.write_text(f"""<!doctype html><html><head><meta charset="utf-8"><title>QIP-Bench Viva Guide</title>
<style>{css}{pyg}</style></head><body>{cover}{toc_page}{body}</body></html>""", encoding="utf-8")

candidates = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              shutil.which("google-chrome") or "", shutil.which("chromium") or ""]
chrome = next(c for c in candidates if c and Path(c).exists())
subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--print-to-pdf-no-header",
                f"--print-to-pdf={OUT_PDF}", HTML.as_uri()], check=True, capture_output=True, timeout=120)
print("pdf ->", OUT_PDF, round(OUT_PDF.stat().st_size / 1024), "KB")
