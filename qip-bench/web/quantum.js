/* Quantum visual layer: entangled-particle background, Bloch sphere, live shot replay, count-ups.
   Everything is driven by real pipeline data; motion is disabled under prefers-reduced-motion. */
const Q = (() => {
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const cssVar = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
  const dpr = () => Math.min(window.devicePixelRatio || 1, 2);

  function fitCanvas(cv) {
    const r = cv.getBoundingClientRect();
    const w = Math.max(1, Math.round(r.width * dpr())), h = Math.max(1, Math.round(r.height * dpr()));
    if (cv.width !== w || cv.height !== h) { cv.width = w; cv.height = h; }
    const g = cv.getContext("2d");
    g.setTransform(dpr(), 0, 0, dpr(), 0, 0);
    return { g, w: r.width, h: r.height };
  }

  function hexToRgb(hex) {
    const m = hex.replace("#", "").match(/.{2}/g);
    return m ? m.map((x) => parseInt(x, 16)) : [57, 135, 229];
  }

  /* ------------------------------------------------------------ background: qubits + entanglement */
  function background(cv) {
    const N = Math.min(70, Math.round(innerWidth / 22));
    const pts = Array.from({ length: N }, () => ({
      x: Math.random(), y: Math.random(), vx: (Math.random() - .5) * 2e-4, vy: (Math.random() - .5) * 2e-4,
      phase: Math.random() * 6.283, w: .6 + Math.random() * 1.6,
    }));
    let mouse = { x: -1, y: -1 };
    addEventListener("pointermove", (e) => { mouse = { x: e.clientX / innerWidth, y: e.clientY / innerHeight }; });
    function frame(t) {
      const { g, w, h } = fitCanvas(cv);
      g.clearRect(0, 0, w, h);
      const [r, gg, b] = hexToRgb(cssVar("--accent"));
      const [r2, g2, b2] = hexToRgb(cssVar("--neqr"));
      for (const p of pts) {
        if (!reduced) {
          p.x += p.vx; p.y += p.vy; p.phase += .012 * p.w;
          if (p.x < 0 || p.x > 1) p.vx *= -1;
          if (p.y < 0 || p.y > 1) p.vy *= -1;
          const dx = p.x - mouse.x, dy = p.y - mouse.y, d2 = dx * dx + dy * dy;
          if (d2 < .01) { p.x += dx * .01; p.y += dy * .01; }
        }
      }
      for (let i = 0; i < N; i++) for (let j = i + 1; j < N; j++) {
        const a = pts[i], c = pts[j];
        const dx = (a.x - c.x) * w, dy = (a.y - c.y) * h, d = Math.hypot(dx, dy);
        if (d < 150) {
          const pulse = .5 + .5 * Math.sin(a.phase - c.phase);
          g.strokeStyle = `rgba(${r},${gg},${b},${(1 - d / 150) * .22 * pulse})`;
          g.lineWidth = 1;
          g.beginPath(); g.moveTo(a.x * w, a.y * h); g.lineTo(c.x * w, c.y * h); g.stroke();
        }
      }
      for (const p of pts) {
        const s = Math.sin(p.phase);               // superposition: colour mixes between |0> and |1> hues
        const m = (s + 1) / 2;
        g.fillStyle = `rgba(${Math.round(r + (r2 - r) * m)},${Math.round(gg + (g2 - gg) * m)},${Math.round(b + (b2 - b) * m)},.55)`;
        g.beginPath(); g.arc(p.x * w, p.y * h, 1.6 + Math.abs(s) * 1.4, 0, 6.283); g.fill();
      }
      if (!reduced && !document.hidden) requestAnimationFrame(frame);
    }
    document.addEventListener("visibilitychange", () => { if (!document.hidden && !reduced) requestAnimationFrame(frame); });
    requestAnimationFrame(frame);
  }

  /* ------------------------------------------------------------ Bloch sphere */
  class Bloch {
    constructor(cv, opts = {}) {
      this.cv = cv; this.yaw = -.6; this.pitch = .35;
      this.theta = 0; this.phi = 0; this.tTheta = 0; this.tPhi = 0;
      this.trail = []; this.precess = !!opts.precess; this.label = "";
      this.autoSpin = opts.autoSpin ?? true;
      let drag = null;
      cv.addEventListener("pointerdown", (e) => { drag = { x: e.clientX, y: e.clientY, yaw: this.yaw, pitch: this.pitch }; cv.setPointerCapture(e.pointerId); });
      cv.addEventListener("pointermove", (e) => {
        if (!drag) return;
        this.yaw = drag.yaw + (e.clientX - drag.x) * .01;
        this.pitch = Math.max(-1.3, Math.min(1.3, drag.pitch + (e.clientY - drag.y) * .01));
        this.autoSpin = false;
      });
      cv.addEventListener("pointerup", () => { drag = null; });
      cv.style.cursor = "grab";
      this.loop = this.loop.bind(this);
      requestAnimationFrame(this.loop);
    }
    set(theta, phi = 0, label = "") { this.tTheta = theta; this.tPhi = phi; this.label = label; if (reduced) { this.theta = theta; this.phi = phi; } }
    project(x, y, z, R, cx, cy) {
      const cyw = Math.cos(this.yaw), syw = Math.sin(this.yaw);
      const x1 = x * cyw - y * syw, y1 = x * syw + y * cyw;          // yaw about z
      const cp = Math.cos(this.pitch), sp = Math.sin(this.pitch);
      const y2 = y1 * cp - z * sp, z2 = y1 * sp + z * cp;             // pitch about screen x
      return { X: cx + x1 * R, Y: cy - z2 * R, depth: y2 };
    }
    loop(t) {
      if (!this.cv.isConnected) return;
      const vis = this.cv.offsetParent !== null;
      if (vis) {
        if (this.precess && !reduced) { this.tPhi += .02; this.tTheta = 1.0 + .35 * Math.sin(t / 1800); }
        if (this.autoSpin && !reduced) this.yaw += .002;
        const k = reduced ? 1 : .12;
        this.theta += (this.tTheta - this.theta) * k;
        let dp = this.tPhi - this.phi;
        this.phi += dp * k;
        this.draw();
      }
      requestAnimationFrame(this.loop);
    }
    draw() {
      const { g, w, h } = fitCanvas(this.cv);
      const R = Math.min(w, h) * .36, cx = w / 2, cy = h / 2 + 4;
      const ink = cssVar("--muted"), acc = cssVar("--accent"), alt = cssVar("--neqr"), border = cssVar("--border");
      g.clearRect(0, 0, w, h);
      const grad = g.createRadialGradient(cx - R * .35, cy - R * .4, R * .1, cx, cy, R);
      grad.addColorStop(0, acc + "33"); grad.addColorStop(1, acc + "05");
      g.fillStyle = grad; g.beginPath(); g.arc(cx, cy, R, 0, 6.283); g.fill();
      g.strokeStyle = border; g.lineWidth = 1.2; g.beginPath(); g.arc(cx, cy, R, 0, 6.283); g.stroke();
      const ring = (fn, color, dash) => {
        g.setLineDash(dash || []); g.strokeStyle = color; g.beginPath();
        for (let i = 0; i <= 96; i++) {
          const a = (i / 96) * 6.283, p = fn(a);
          const P = this.project(p[0], p[1], p[2], R, cx, cy);
          i ? g.lineTo(P.X, P.Y) : g.moveTo(P.X, P.Y);
        }
        g.stroke(); g.setLineDash([]);
      };
      ring((a) => [Math.cos(a), Math.sin(a), 0], border, [3, 4]);           // equator
      ring((a) => [Math.cos(a), 0, Math.sin(a)], border, [2, 5]);           // XZ meridian (FRQI plane)
      const axis = (v, lbl) => {
        const O = this.project(0, 0, 0, R, cx, cy), P = this.project(v[0] * 1.18, v[1] * 1.18, v[2] * 1.18, R, cx, cy);
        g.strokeStyle = ink + "88"; g.beginPath(); g.moveTo(O.X, O.Y); g.lineTo(P.X, P.Y); g.stroke();
        g.fillStyle = ink; g.font = "600 12px Inter, sans-serif"; g.textAlign = "center"; g.textBaseline = "middle";
        g.fillText(lbl, P.X + (P.X - O.X) * .12, P.Y + (P.Y - O.Y) * .12);
      };
      axis([0, 0, 1], "|0⟩"); axis([0, 0, -1], "|1⟩"); axis([1, 0, 0], "|+⟩"); axis([0, 1, 0], "|+i⟩");
      const sx = Math.sin(this.theta) * Math.cos(this.phi), sy = Math.sin(this.theta) * Math.sin(this.phi), sz = Math.cos(this.theta);
      this.trail.push([sx, sy, sz]); if (this.trail.length > 40) this.trail.shift();
      this.trail.forEach((p, i) => {
        const P = this.project(p[0], p[1], p[2], R, cx, cy);
        g.fillStyle = alt; g.globalAlpha = (i / this.trail.length) * .5;
        g.beginPath(); g.arc(P.X, P.Y, 2, 0, 6.283); g.fill();
      });
      g.globalAlpha = 1;
      const O = this.project(0, 0, 0, R, cx, cy), S = this.project(sx, sy, sz, R, cx, cy);
      const proj = this.project(sx, sy, 0, R, cx, cy);
      g.setLineDash([2, 3]); g.strokeStyle = alt + "99";
      g.beginPath(); g.moveTo(S.X, S.Y); g.lineTo(proj.X, proj.Y); g.stroke(); g.setLineDash([]);
      g.strokeStyle = alt; g.lineWidth = 3; g.lineCap = "round";
      g.beginPath(); g.moveTo(O.X, O.Y); g.lineTo(S.X, S.Y); g.stroke();
      g.shadowColor = alt; g.shadowBlur = 14; g.fillStyle = alt;
      g.beginPath(); g.arc(S.X, S.Y, 6, 0, 6.283); g.fill(); g.shadowBlur = 0;
      g.lineWidth = 1;
      if (this.label) {
        g.fillStyle = cssVar("--ink"); g.font = "500 12px 'JetBrains Mono', monospace"; g.textAlign = "center";
        g.fillText(this.label, cx, h - 10);
      }
    }
  }

  /* ------------------------------------------------------------ measurement replay */
  class Replay {
    constructor({ canvas, hist, counter, size, encoding, measurement, finalPixels }) {
      Object.assign(this, { canvas, hist, counter, size, encoding, m: measurement, finalPixels });
      const L = measurement.layout;
      this.N = size * size; this.n = L.position; this.q = L.color;
      this.idx = measurement.index; this.wt = measurement.weight;
      this.total = measurement.exact ? 4096 : measurement.shots;
      this.outcomes = this.buildOutcomes();
      this.seen = new Float64Array(this.idx.length);
      this.reset();
      this.ro = new ResizeObserver(() => {          // tab shown or layout changed: (re)draw
        if (!this.canvas.offsetParent) return;
        if (this.pending) this.play();
        else if (!this.animating) { this.drawImage(); this.drawHist(); }
      });
      this.ro.observe(this.canvas);
    }
    dispose() { this.ro.disconnect(); cancelAnimationFrame(this.raf); }
    buildOutcomes() {
      const out = new Int32Array(this.total);
      if (this.m.exact) {                                  // sample from |psi|^2
        const cum = []; let s = 0; for (const w of this.wt) cum.push(s += w);
        for (let k = 0; k < this.total; k++) {
          const u = Math.random() * s; let lo = 0, hi = cum.length - 1;
          while (lo < hi) { const mid = (lo + hi) >> 1; cum[mid] < u ? lo = mid + 1 : hi = mid; }
          out[k] = lo;
        }
      } else {                                             // the real shots, in random order
        let k = 0;
        this.wt.forEach((c, i) => { for (let j = 0; j < Math.round(c) && k < out.length; j++) out[k++] = i; });
        for (let i = k - 1; i > 0; i--) { const j = (Math.random() * (i + 1)) | 0; [out[i], out[j]] = [out[j], out[i]]; }
        this.total = k;
      }
      return out;
    }
    reset() {
      this.done = 0; this.seen.fill(0);
      const levels = this.encoding === "neqr" ? 2 ** this.q : 2;
      this.table = new Float64Array(levels * this.N);
    }
    add(k) {
      const end = Math.min(this.total, this.done + k);
      const mask = this.N - 1, levels = this.encoding === "neqr" ? 2 ** this.q : 2;
      for (; this.done < end; this.done++) {
        const o = this.outcomes[this.done], basis = this.idx[o];
        this.seen[o]++;
        const pos = basis & mask;
        const color = this.encoding === "amplitude" ? 0 : (basis >> this.n) & (levels - 1);
        this.table[color * this.N + pos]++;
      }
    }
    image() {
      const N = this.N, img = new Float64Array(N), valid = new Uint8Array(N);
      if (this.encoding === "frqi") {
        for (let i = 0; i < N; i++) {
          const n0 = this.table[i], n1 = this.table[N + i];
          if (n0 + n1 > 0) { valid[i] = 1; img[i] = (2 / Math.PI) * Math.asin(Math.sqrt(n1 / (n0 + n1))); }
        }
      } else if (this.encoding === "neqr") {
        const L = 2 ** this.q;
        for (let i = 0; i < N; i++) {
          let best = -1, arg = 0;
          for (let v = 0; v < L; v++) { const c = this.table[v * N + i]; if (c > best) { best = c; arg = v; } }
          if (best > 0) { valid[i] = 1; img[i] = arg / (L - 1); }
        }
      } else {
        const tot = Math.max(1, this.done), norm = this.m.layout.norm || 1;
        for (let i = 0; i < N; i++) { const c = this.table[i]; if (c > 0) { valid[i] = 1; img[i] = Math.min(1, norm * Math.sqrt(c / tot)); } }
      }
      return { img, valid };
    }
    drawImage() {
      const { g, w } = fitCanvas(this.canvas);
      const s = this.size, cell = w / s, { img, valid } = this.image();
      const fin = this.done >= this.total && this.finalPixels;
      g.clearRect(0, 0, w, w);
      for (let r = 0; r < s; r++) for (let c = 0; c < s; c++) {
        const i = r * s + c;
        const v = fin ? this.finalPixels[r][c] : img[i];
        if (valid[i] || fin) { const k = Math.round(v * 255); g.fillStyle = `rgb(${k},${k},${k})`; }
        else { g.fillStyle = cssVar("--surface-2"); }
        g.fillRect(c * cell, r * cell, Math.ceil(cell), Math.ceil(cell));
        if (!valid[i] && !fin) {                           // unmeasured pixel: still in superposition
          g.fillStyle = cssVar("--accent") + "55";
          const t = performance.now() / 300 + i;
          g.beginPath(); g.arc((c + .5) * cell, (r + .5) * cell, cell * (.12 + .06 * Math.sin(t)), 0, 6.283); g.fill();
        }
      }
    }
    drawHist() {
      const { g, w, h } = fitCanvas(this.hist);
      g.clearRect(0, 0, w, h);
      const order = [...this.wt.keys()].sort((a, b) => this.wt[b] - this.wt[a]).slice(0, 32);
      const max = Math.max(1, ...order.map((i) => this.seen[i]));
      const bw = w / Math.max(order.length, 1);
      const bits = this.n + this.q + (this.m.layout.ancilla || 0);
      const acc = cssVar("--accent"), ink = cssVar("--muted");
      order.forEach((i, k) => {
        const v = this.seen[i] / max, bh = v * (h - 26);
        g.fillStyle = acc; g.globalAlpha = .35 + .65 * v;
        const x = k * bw + 1, y = h - 18 - bh;
        g.beginPath(); g.roundRect ? g.roundRect(x, y, Math.max(1, bw - 2), bh, [3, 3, 0, 0]) : g.rect(x, y, bw - 2, bh); g.fill();
      });
      g.globalAlpha = 1;
      g.fillStyle = ink; g.font = "10px 'JetBrains Mono', monospace"; g.textAlign = "left";
      if (order.length) g.fillText(`|${this.idx[order[0]].toString(2).padStart(bits, "0")}⟩  most frequent basis state`, 2, h - 4);
    }
    play(duration = 2600) {
      if (!this.canvas.offsetParent) { this.pending = true; return; }   // hidden tab: play when shown
      this.pending = false;
      this.animating = true;
      this.reset();
      cancelAnimationFrame(this.raf);
      const t0 = performance.now();
      const step = (t) => {
        const f = reduced ? 1 : Math.min(1, (t - t0) / duration);
        const target = Math.round(this.total * (f * f * (3 - 2 * f)));
        this.add(target - this.done);
        this.drawImage(); this.drawHist();
        this.counter.textContent = `${this.done.toLocaleString()} / ${this.total.toLocaleString()} shots` +
          (this.m.exact ? " · sampled from exact |ψ|²" : " · replaying measured outcomes");
        if (this.done < this.total) this.raf = requestAnimationFrame(step);
        else { this.animating = false; this.drawImage(); }
      };
      this.raf = requestAnimationFrame(step);
    }
  }

  /* ------------------------------------------------------------ count-up */
  function countUp(root = document) {
    root.querySelectorAll("[data-count]").forEach((el) => {
      const target = parseFloat(el.dataset.count), dec = +el.dataset.dec || 0, suf = el.dataset.suffix || "";
      if (!Number.isFinite(target) || reduced) { el.textContent = el.dataset.final; return; }
      const t0 = performance.now(), dur = 900;
      const tick = (t) => {
        const f = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - f, 3);
        el.textContent = (target * e).toLocaleString(undefined, { minimumFractionDigits: dec, maximumFractionDigits: dec }) + suf;
        if (f < 1) requestAnimationFrame(tick); else el.textContent = el.dataset.final;
      };
      requestAnimationFrame(tick);
    });
  }

  /* ------------------------------------------------------------ stage loader */
  function stages(el) {
    const items = [...el.querySelectorAll("li")];
    let timer = null;
    return {
      start() {
        items.forEach((li) => li.classList.remove("done", "active"));
        let k = 0;
        items[0].classList.add("active");
        clearInterval(timer);
        timer = setInterval(() => {
          if (k < items.length - 2) { items[k].classList.replace("active", "done"); items[++k].classList.add("active"); }
        }, 260);
      },
      finish(ok = true) {
        clearInterval(timer);
        items.forEach((li) => { li.classList.remove("active"); if (ok) li.classList.add("done"); });
      },
    };
  }

  return { background, Bloch, Replay, countUp, stages, reduced };
})();
