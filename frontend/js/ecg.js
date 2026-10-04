/**
 * CardioHealth AI - Real-Time Clinical ECG Waveform Canvas Visualizer
 * Accurately simulates Lead II cardiac rhythm trace adapted for clinical light paper and ICU dark monitors.
 */

class ECGVisualizer {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext("2d");
    this.animationId = null;
    this.x = 0;
    this.prevY = 0;
    this.bpm = 72;
    this.speed = 2.0;

    this.resize();
    window.addEventListener("resize", () => this.resize());
    
    // Listen for theme changes to adapt grid and trace colors
    const observer = new MutationObserver(() => this.updateThemeColors());
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
    this.updateThemeColors();

    this.start();
  }

  updateThemeColors() {
    const isDark = document.documentElement.getAttribute("data-theme") === "dark";
    if (isDark) {
      this.gridColor = "rgba(56, 189, 248, 0.08)";
      this.traceColor = "#38bdf8";
      this.glowColor = "rgba(56, 189, 248, 0.35)";
      this.clearColor = "rgba(2, 6, 23, 0.25)";
    } else {
      // Authentic Medical Pink Paper Grid
      this.gridColor = "rgba(239, 68, 68, 0.12)";
      this.traceColor = "#b91c1c"; // Deep clinical cardiology crimson
      this.glowColor = "rgba(185, 28, 28, 0.15)";
      this.clearColor = "rgba(255, 245, 245, 0.3)";
    }
    this.drawGrid();
  }

  resize() {
    if (!this.canvas) return;
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.width = rect.width;
    this.height = rect.height || 200;
    this.canvas.width = this.width;
    this.canvas.height = this.height;
    this.baselineY = this.height / 2;
    this.prevY = this.baselineY;
    this.drawGrid();
  }

  setBpm(bpm) {
    this.bpm = Math.max(40, Math.min(200, bpm));
  }

  drawGrid() {
    if (!this.ctx) return;
    const ctx = this.ctx;
    ctx.strokeStyle = this.gridColor || "rgba(239, 68, 68, 0.12)";
    ctx.lineWidth = 1;

    // Standard clinical 1mm / 5mm equivalent ECG grid
    for (let x = 0; x < this.width; x += 15) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, this.height);
      ctx.stroke();
    }
    for (let y = 0; y < this.height; y += 15) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(this.width, y);
      ctx.stroke();
    }
  }

  getEcgSample(t) {
    const cyclePos = t % 1.0;
    let val = 0;

    // P-wave (Atrial depolarization)
    if (cyclePos > 0.1 && cyclePos < 0.2) {
      const pPos = (cyclePos - 0.1) / 0.1;
      val = Math.sin(pPos * Math.PI) * 0.16;
    }
    // PR segment
    else if (cyclePos >= 0.2 && cyclePos < 0.26) {
      val = 0;
    }
    // QRS complex
    else if (cyclePos >= 0.26 && cyclePos < 0.28) {
      val = -0.16; // Q wave
    } else if (cyclePos >= 0.28 && cyclePos < 0.32) {
      val = 0.98;  // R wave sharp peak
    } else if (cyclePos >= 0.32 && cyclePos < 0.35) {
      val = -0.32; // S wave
    }
    // ST segment
    else if (cyclePos >= 0.35 && cyclePos < 0.44) {
      val = 0.01;
    }
    // T-wave (Ventricular repolarization)
    else if (cyclePos >= 0.44 && cyclePos < 0.6) {
      const tPos = (cyclePos - 0.44) / 0.16;
      val = Math.sin(tPos * Math.PI) * 0.3;
    }
    else {
      val = (Math.random() - 0.5) * 0.015; // Natural physiological baseline drift
    }

    return val;
  }

  animate() {
    if (!this.ctx) return;
    const ctx = this.ctx;

    const pixelsPerBeat = 125;
    const clearWidth = 20;

    ctx.fillStyle = this.clearColor || "rgba(255, 245, 245, 0.3)";
    ctx.fillRect(this.x, 0, clearWidth, this.height);

    const cycleProgress = (this.x / pixelsPerBeat) % 1.0;
    const signal = this.getEcgSample(cycleProgress);
    const currentY = this.baselineY - (signal * (this.height * 0.44));

    ctx.shadowBlur = 4;
    ctx.shadowColor = this.glowColor;
    ctx.strokeStyle = this.traceColor;
    ctx.lineWidth = 2.2;
    ctx.lineCap = "round";

    ctx.beginPath();
    ctx.moveTo(this.x, this.prevY);
    ctx.lineTo(this.x + this.speed, currentY);
    ctx.stroke();

    ctx.shadowBlur = 0;
    this.prevY = currentY;
    this.x += this.speed;

    if (this.x >= this.width) {
      this.x = 0;
      this.prevY = this.baselineY;
    }

    this.animationId = requestAnimationFrame(() => this.animate());
  }

  start() {
    if (!this.animationId) {
      this.animate();
    }
  }

  stop() {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }
  }
}

window.ECGVisualizer = ECGVisualizer;
