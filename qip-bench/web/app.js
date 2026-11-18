/* QIP-Bench dashboard: talks to the FastAPI service in qipbench/server.py */
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const ENC = { frqi: "FRQI", neqr: "NEQR", amplitude: "Amplitude (QPIE)" };
const encColor = (e) => css({ frqi: "--frqi", neqr: "--neqr", amplitude: "--amp" }[e]);
const fmt = (v, d = 2) => (v == null || Number.isNaN(v)) ? "–" : (Math.abs(v) >= 1000 ? Math.round(v).toLocaleString() : (+v).toFixed(d));

let SUMMARY = null, META = null;
const charts = {};

/* ---------------------------------------------------------------- shell */
$$("#tabs button").forEach((b) => b.addEventListener("click", () => {
  $$("#tabs button").forEach((x) => x.classList.toggle("active", x === b));
  $$(".tab").forEach((t) => t.classList.toggle("active", t.id === b.dataset.tab));
  history.replaceState(null, "", "#" + b.dataset.tab);
}));
const initial = location.hash.slice(1);
if (initial && $(`#tabs button[data-tab="${initial}"]`)) $(`#tabs button[data-tab="${initial}"]`).click();

$("#theme").addEventListener("click", () => {
  const dark = matchMedia("(prefers-color-scheme: dark)").matches;
  const cur = document.documentElement.dataset.theme || (dark ? "dark" : "light");
  document.documentElement.dataset.theme = cur === "dark" ? "light" : "dark";
  try { localStorage.setItem("qip-theme", document.documentElement.dataset.theme); } catch (e) { /* storage blocked */ }
  redrawCharts();
});
try { const t = localStorage.getItem("qip-theme"); if (t) document.documentElement.dataset.theme = t; } catch (e) { /* storage blocked */ }

function chartDefaults() {
  Chart.defaults.font.family = "Inter, system-ui, sans-serif";
  Chart.defaults.color = css("--muted");
  Chart.defaults.borderColor = css("--border");
}

async function api(path, form) {
  const res = await fetch(path, form ? { method: "POST", body: form } : undefined);
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body.detail || res.statusText);
  return body;
}

function showError(id, err) {
  const el = $(id);
  el.hidden = !err;
  el.textContent = err ? "⚠ " + err.message : "";
}

async function busy(btn, fn) {
  const label = btn.textContent;
  btn.disabled = true; btn.textContent = "Simulating…";
  try { await fn(); } finally { btn.disabled = false; btn.textContent = label; }
}

function kpi(label, value, sub = "") {
  const str = String(value);
  const word = /[a-z]{3,}/i.test(str) && !/dB|exact/.test(str);
  const num = str.match(/^([\d,]+(?:\.\d+)?)(\s?(?:dB|s|%))?$/);
  const count = num ? ` data-count="${num[1].replace(/,/g, "")}" data-dec="${(num[1].split(".")[1] || "").length}" data-suffix="${num[2] || ""}" data-final="${str}"` : "";
  return `<div class="kpi"><div class="label">${label}</div><div class="value${word ? " word" : ""}"${count}>${value}</div><div class="sub">${sub}</div></div>`;
}

/* ---------------------------------------------------------------- overview */
function renderOverview() {
  const rk = SUMMARY?.rankings;
  const ofatRuns = (SUMMARY?.ofat || []).reduce((s, r) => s + (r.n || 0), 0);
  const top = (enc, dim) => rk?.[enc]?.[dim]?.[0];
  const k = [
    kpi("Simulated pipeline runs", ofatRuns ? (ofatRuns + 2 * 128 * 6).toLocaleString() : "–", "OFAT sweeps + 2⁷ factorial ×2"),
    kpi("Design factors studied", "11", "across 7 pipeline stages"),
  ];
  if (rk) {
    k.push(kpi("Top quality driver · FRQI", top("frqi", "quality").label, `${fmt(top("frqi", "quality").contribution, 0)}% of PSNR variance`));
    k.push(kpi("Top quality driver · NEQR", top("neqr", "quality").label, `${fmt(top("neqr", "quality").contribution, 0)}% of PSNR variance`));
    k.push(kpi("Top cost driver · FRQI", top("frqi", "efficiency").label, `${fmt(top("frqi", "efficiency").contribution, 0)}% of CNOT variance`));
  }
  $("#kpis").innerHTML = k.join("");
  Q.countUp($("#kpis"));
  drawRanking();
}

function segValue(id) { return $(`${id} button.on`).dataset.v; }
$$(".seg").forEach((seg) => seg.addEventListener("click", (e) => {
  if (e.target.tagName !== "BUTTON") return;
  $$("button", seg).forEach((b) => b.classList.toggle("on", b === e.target));
  drawRanking();
}));

function hatch(color) {
  const c = document.createElement("canvas"); c.width = c.height = 8;
  const g = c.getContext("2d");
  g.strokeStyle = color; g.lineWidth = 2;
  g.beginPath(); g.moveTo(0, 8); g.lineTo(8, 0); g.stroke();
  return g.createPattern(c, "repeat");
}

function drawRanking() {
  const rk = SUMMARY?.rankings;
  if (!rk) return;
  const enc = segValue("#rank-enc"), dim = segValue("#rank-dim");
  const rows = rk[enc][dim];
  const color = encColor(enc);
  charts.rank?.destroy();
  charts.rank = new Chart($("#rank-chart"), {
    type: "bar",
    data: {
      labels: rows.map((r) => r.label),
      datasets: [{
        data: rows.map((r) => r.contribution),
        backgroundColor: rows.map((r) => (r.p_value < 0.05 ? color : hatch(color))),
        borderColor: color, borderWidth: rows.map((r) => (r.p_value < 0.05 ? 0 : 1)),
        borderRadius: 4, barThickness: 18,
      }],
    },
    options: {
      indexAxis: "y", maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: (c) => {
          const r = rows[c.dataIndex];
          return ` ${r.contribution.toFixed(1)}% of variance · effect ${r.effect.toFixed(3)} · p = ${r.p_value.toExponential(1)}`;
        } } },
      },
      scales: { x: { title: { display: true, text: "% of variance explained" }, beginAtZero: true, grid: { color: css("--border") } },
                y: { grid: { display: false } } },
    },
  });
}

async function loadFindings() {
  const { findings } = await api("/api/findings");
  if (!findings.length) return;
  $("#findings").innerHTML = findings.map((f) => `<li>${f.replace(/\*\*(.+?)\*\*/g, "<b>$1</b>")}</li>`).join("");
}

/* ---------------------------------------------------------------- lab */
function fillImageSelects() {
  $$(".image-select").forEach((sel) => {
    const def = sel.closest("#edge-form") ? "blocks" : "camera";
    sel.innerHTML = META.images.map((i) => `<option ${i === def ? "selected" : ""}>${i}</option>`).join("");
  });
}

const labStages = Q.stages($("#lab-stages"));
var replay = null;   // var: read by the tab handler, which can run before this line
$("#replay").addEventListener("click", () => replay?.play());

$("#lab-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const btn = $("button[type=submit]", e.target);
  busy(btn, async () => {
    showError("#lab-error", null);
    labStages.start();
    try {
      const r = await api("/api/pipeline", new FormData(e.target));
      labStages.finish(true);
      replay?.dispose();
      replay = new Q.Replay({ canvas: $("#replay-img"), hist: $("#replay-hist"), counter: $("#replay-count"),
        size: r.config.size, encoding: r.config.encoding, measurement: r.measurement, finalPixels: r.pixels.reconstructed });
      replay.play();
      explorer.load(r);
      $$(".pipeline-strip figure").forEach((f, i) => { f.classList.remove("pop"); void f.offsetWidth; f.style.animationDelay = `${i * 90}ms`; f.classList.add("pop"); });
      $("#img-source").src = r.images.source;
      $("#img-pre").src = r.images.preprocessed;
      $("#img-expected").src = r.images.expected;
      $("#img-recon").src = r.images.reconstructed;
      $("#img-error").src = r.images.error;
      const m = r.metrics;
      $("#lab-metrics").innerHTML = [
        kpi("PSNR", fmt(m.psnr, 1) + " dB", m.psnr >= 60 ? "exact (capped)" : "vs expected"),
        kpi("SSIM", fmt(m.ssim, 3), m.success ? "meets 0.90 target" : "below 0.90 target"),
        kpi("Exact grey levels", fmt(100 * m.level_accuracy, 0) + "%", `max |error| ${fmt(r.max_error, 3)}`),
        kpi("Distribution fidelity", fmt(m.fidelity, 3), `TVD ${fmt(m.tvd, 3)}`),
        kpi("Qubits", m.qubits, `coverage ${fmt(100 * m.coverage, 0)}%`),
        kpi("CNOTs", fmt(m.cx, 0), `${fmt(m.gates, 0)} gates total`),
        kpi("Depth", fmt(m.depth, 0), `logical ${fmt(m.logical_depth, 0)}`),
        kpi("Runtime", fmt(m.total_s, 2) + " s", `sim ${fmt(m.simulate_s, 2)} s`),
      ].join("");
      Q.countUp($("#lab-metrics"));
      $("#lab-circuit").textContent = r.circuit || `Circuit too large to draw (${m.qubits} qubits, ${m.gates} transpiled gates).`;
    } catch (err) { labStages.finish(false); showError("#lab-error", err); }
  });
});

/* ---------------------------------------------------------------- compare */
$("#cmp-form").addEventListener("submit", (e) => {
  e.preventDefault();
  busy($("button[type=submit]", e.target), async () => {
    showError("#cmp-error", null);
    try {
      const r = await api("/api/compare", new FormData(e.target));
      const cards = [`<div class="card cmp"><h3>Expected</h3><img src="${r.expected}" alt="expected image"><p class="muted small">Preprocessed image loaded into each circuit</p></div>`];
      const rows = [];
      for (const [enc, v] of Object.entries(r.results)) {
        if (v.error) {
          cards.push(`<div class="card cmp"><h3><span class="dot" style="background:${encColor(enc)}"></span>${ENC[enc]}</h3><p class="muted">${v.error}</p></div>`);
          continue;
        }
        const m = v.metrics;
        cards.push(`<div class="card cmp"><h3><span class="dot" style="background:${encColor(enc)}"></span>${ENC[enc]}</h3>
          <img src="${v.reconstructed}" alt="${ENC[enc]} reconstruction">
          <dl><dt>PSNR</dt><dd>${fmt(m.psnr, 1)} dB</dd><dt>SSIM</dt><dd>${fmt(m.ssim, 3)}</dd>
          <dt>Qubits</dt><dd>${m.qubits}</dd><dt>CNOTs</dt><dd>${fmt(m.cx, 0)}</dd><dt>Depth</dt><dd>${fmt(m.depth, 0)}</dd></dl></div>`);
        rows.push(`<tr><td>${ENC[enc]}</td><td>${m.qubits}</td><td>${fmt(m.cx, 0)}</td><td>${fmt(m.depth, 0)}</td><td>${fmt(m.psnr, 1)}</td><td>${fmt(m.ssim, 3)}</td>
          <td>${fmt(100 * m.level_accuracy, 0)}%</td><td>${fmt(m.fidelity, 3)}</td><td>${fmt(m.total_s, 2)}</td></tr>`);
      }
      $("#cmp-out").innerHTML = cards.join("");
      $$("#cmp-out .card").forEach((c, i) => { c.style.animationDelay = `${i * 110}ms`; c.classList.add("pop"); });
      $("#cmp-table").innerHTML = `<thead><tr><th>Encoding</th><th>Qubits</th><th>CNOTs</th><th>Depth</th><th>PSNR (dB)</th><th>SSIM</th><th>Exact levels</th><th>Fidelity</th><th>Runtime (s)</th></tr></thead><tbody>${rows.join("")}</tbody>`;
    } catch (err) { showError("#cmp-error", err); }
  });
});

/* ---------------------------------------------------------------- edges */
$("#edge-form").addEventListener("submit", (e) => {
  e.preventDefault();
  busy($("button[type=submit]", e.target), async () => {
    showError("#edge-error", null);
    try {
      const r = await api("/api/edges", new FormData(e.target));
      const labels = { input: "Input", quantum_gradient: "Quantum |∇|", classical_gradient: "Classical |∇|",
        quantum_edges: "Quantum edges", classical_edges: "Classical edges", sobel_edges: "Sobel edges" };
      $("#edge-imgs").innerHTML = Object.entries(labels)
        .map(([k, l], i) => `<figure class="scan" style="--d:${i * 120}ms"><div class="scan-wrap"><img src="${r.images[k]}" alt="${l}"></div><figcaption>${l}</figcaption></figure>`).join("");
      const m = r.metrics;
      $("#edge-metrics").innerHTML = [
        kpi("Edge F1 vs exact", fmt(m.edge_f1, 3), `IoU ${fmt(m.edge_iou, 3)}`),
        kpi("Precision / recall", `${fmt(m.edge_precision, 2)} / ${fmt(m.edge_recall, 2)}`),
        kpi("F1 vs Sobel", fmt(m.sobel_f1, 3), "classical operator"),
        kpi("Gradient MAE", fmt(m.gradient_mae, 3), `PSNR ${fmt(m.gradient_psnr, 1)} dB`),
        kpi("Qubits", m.qubits, "data + 1 ancilla"),
        kpi("CNOTs / circuit", fmt(m.cx, 0), `depth ${fmt(m.depth, 0)}`),
        kpi("Shots used", m.shots_total ? fmt(m.shots_total, 0) : "exact", "2 circuits (H + V scan)"),
      ].join("");
      Q.countUp($("#edge-metrics"));
    } catch (err) { showError("#edge-error", err); }
  });
});

/* ---------------------------------------------------------------- research */
function renderResearch() {
  if (!SUMMARY?.studies) {
    $("#study-question").textContent = "No results yet. Run `python -m qipbench run`, then reload.";
    return;
  }
  $("#study-select").innerHTML = SUMMARY.studies.map((s) => `<option value="${s.name}">${s.label}</option>`).join("");
  $("#gallery").innerHTML = (SUMMARY.figures || [])
    .map((f) => `<a href="/figures/${f}" target="_blank" rel="noopener"><img src="/figures/${f}" alt="${f}" loading="lazy"></a>`).join("");
  drawStudy();
}

function drawStudy() {
  const study = $("#study-select").value, metric = $("#metric-select").value;
  const meta = SUMMARY.studies.find((s) => s.name === study);
  $("#study-question").textContent = meta.question;
  const rows = SUMMARY.ofat.filter((r) => r.study === study);
  const levels = [...new Set(rows.map((r) => String(r.level)))];
  const encs = [...new Set(rows.map((r) => r.encoding))];
  const logScale = ["cx", "depth", "total_s"].includes(metric);
  charts.study?.destroy();
  charts.study = new Chart($("#study-chart"), {
    type: "line",
    data: {
      labels: levels,
      datasets: encs.map((e) => ({
        label: ENC[e], borderColor: encColor(e), backgroundColor: encColor(e), borderWidth: 2,
        pointRadius: 4, pointHoverRadius: 6, pointBorderColor: css("--surface"), pointBorderWidth: 2,
        data: levels.map((l) => rows.find((r) => r.encoding === e && String(r.level) === l)?.[metric] ?? null),
      })),
    },
    options: {
      maintainAspectRatio: false, interaction: { mode: "index", intersect: false },
      plugins: { legend: { position: "top", align: "end", labels: { usePointStyle: true, boxWidth: 8 } },
                 tooltip: { callbacks: { label: (c) => ` ${c.dataset.label}: ${fmt(c.parsed.y, 3)}` } } },
      scales: { x: { title: { display: true, text: meta.label }, grid: { display: false } },
                y: { type: logScale ? "logarithmic" : "linear", title: { display: true, text: $("#metric-select").selectedOptions[0].text } } },
    },
  });
  const cols = ["encoding", "level", "qubits", "cx", "depth", "psnr", "psnr_ci", "ssim", "e2e_psnr", "coverage", "success", "psnr_sd", "total_s", "n"];
  $("#study-table").innerHTML = `<thead><tr>${cols.map((c) => `<th>${c}</th>`).join("")}</tr></thead><tbody>` +
    rows.map((r) => `<tr>${cols.map((c) => `<td>${typeof r[c] === "number" ? fmt(r[c], 3) : (ENC[r[c]] || r[c])}</td>`).join("")}</tr>`).join("") + "</tbody>";
}
$("#study-select").addEventListener("change", drawStudy);
$("#metric-select").addEventListener("change", drawStudy);

function redrawCharts() {
  chartDefaults();
  if (SUMMARY) { drawRanking(); if (SUMMARY.studies) drawStudy(); }
}

/* ---------------------------------------------------------------- qubit explorer */
const explorer = (() => {
  const cv = $("#explorer-img"), out = $("#explorer-state");
  const bloch = new Q.Bloch($("#explorer-bloch"), { autoSpin: true });
  let px = null, enc = "frqi", bits = 8, hover = -1, scan = 0, timer = null;

  function draw() {
    if (!px) return;
    const s = px.length, { g, w } = fitPixel(cv);
    const cell = w / s;
    for (let r = 0; r < s; r++) for (let c = 0; c < s; c++) {
      const k = Math.round(px[r][c] * 255);
      g.fillStyle = `rgb(${k},${k},${k})`; g.fillRect(c * cell, r * cell, Math.ceil(cell), Math.ceil(cell));
    }
    const i = hover >= 0 ? hover : scan, r = Math.floor(i / s), c = i % s;
    g.strokeStyle = css("--neqr"); g.lineWidth = 3; g.strokeRect(c * cell + 1.5, r * cell + 1.5, cell - 3, cell - 3);
  }
  function fitPixel(c) {
    const rect = c.getBoundingClientRect(), d = Math.min(devicePixelRatio || 1, 2);
    c.width = rect.width * d; c.height = rect.width * d;
    const g = c.getContext("2d"); g.setTransform(d, 0, 0, d, 0, 0);
    return { g, w: rect.width };
  }
  function show(i) {
    const s = px.length, r = Math.floor(i / s), c = i % s, v = px[r][c];
    const nPos = Math.log2(s * s), pos = i.toString(2).padStart(nPos, "0");
    if (enc === "neqr") {
      const level = Math.round(v * (2 ** bits - 1)), code = level.toString(2).padStart(bits, "0");
      bloch.set(code[0] === "1" ? Math.PI : 0, 0, `MSB colour qubit = |${code[0]}⟩`);
      out.innerHTML = `<div><span>pixel</span> (${r}, ${c}) · index ${i}</div>
        <div><span>grey level</span> ${level} / ${2 ** bits - 1}</div>
        <div><span>state</span> |${code}⟩<sub>colour</sub> ⊗ |${pos}⟩<sub>position</sub></div>
        <div class="chips">${[...code].map((b) => `<i class="${b === "1" ? "on" : ""}">${b}</i>`).join("")}</div>`;
    } else {
      const th = (Math.PI / 2) * v;
      bloch.set(2 * th, 0, `cos θ|0⟩ + sin θ|1⟩,  θ = ${th.toFixed(3)}`);
      out.innerHTML = `<div><span>pixel</span> (${r}, ${c}) · index ${i}</div>
        <div><span>intensity</span> ${v.toFixed(4)} → θ = (π/2)·I = ${th.toFixed(4)} rad</div>
        <div><span>colour qubit</span> ${Math.cos(th).toFixed(3)}|0⟩ + ${Math.sin(th).toFixed(3)}|1⟩</div>
        <div><span>entangled with</span> |${pos}⟩<sub>position</sub> · amplitude 1/√${s * s}</div>
        ${enc === "amplitude" ? '<div class="muted">QPIE stores this pixel as amplitude cᵢ = Iᵢ/‖I‖. Shown here: the equivalent FRQI qubit.</div>' : ""}`;
    }
    draw();
  }
  cv.addEventListener("pointermove", (e) => {
    if (!px) return;
    const rect = cv.getBoundingClientRect(), s = px.length;
    const c = Math.min(s - 1, Math.floor(((e.clientX - rect.left) / rect.width) * s));
    const r = Math.min(s - 1, Math.floor(((e.clientY - rect.top) / rect.height) * s));
    const i = r * s + c;
    if (i !== hover) { hover = i; show(i); }
  });
  cv.addEventListener("pointerleave", () => { hover = -1; });
  return {
    load(r) {
      px = r.pixels.loaded; enc = r.config.encoding; bits = r.config.bit_depth; scan = 0; hover = -1;
      show(0);
      clearInterval(timer);
      if (!Q.reduced) timer = setInterval(() => { if (hover < 0 && cv.offsetParent) { scan = (scan + 1) % (px.length ** 2); show(scan); } }, 1400);
    },
  };
})();

/* ---------------------------------------------------------------- boot */
Q.background($("#qbg"));
new Q.Bloch($("#hero-bloch"), { precess: true });
$$("[data-goto]").forEach((b) => b.addEventListener("click", () => $(`#tabs button[data-tab="${b.dataset.goto}"]`).click()));

(async function boot() {
  chartDefaults();
  META = await api("/api/meta");
  fillImageSelects();
  try {
    SUMMARY = await api("/api/results");
  } catch (e) {
    $("#kpis").innerHTML = kpi("Results", "not generated", "run python -m qipbench run");
  }
  if (SUMMARY) { renderOverview(); renderResearch(); loadFindings(); }
  $("#lab-form").requestSubmit();
})();
