/**
 * CardioAI - Real-Time ECG Waveform Canvas Visualizer
 * Simulates a realistic cardiac lead II rhythm trace (P-wave, QRS complex, T-wave).
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
    this.speed = 2.2;
    this.traceColor = "#06b6d4";
    this.glowColor = "rgba(6, 182, 212, 0.4)";

    this.resize();
    window.addEventListener("resize", () => this.resize());
    this.start();
  }

  resize() {
    if (!this.canvas) return;
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.width = rect.width;
    this.height = rect.height || 180;
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
    const ctx = this.ctx;
    ctx.strokeStyle = "rgba(6, 182, 212, 0.08)";
    ctx.lineWidth = 1;

    // Small medical grid squares (20px)
    for (let x = 0; x < this.width; x += 20) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, this.height);
      ctx.stroke();
    }
    for (let y = 0; y < this.height; y += 20) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(this.width, y);
      ctx.stroke();
    }
  }

  getEcgSample(t) {
    // Standard normalized cardiac cycle (P - Q - R - S - T)
    const cyclePos = t % 1.0;
    
    // Baseline
    let val = 0;

    // P-wave (Atrial depolarization)
    if (cyclePos > 0.1 && cyclePos < 0.2) {
      const pPos = (cyclePos - 0.1) / 0.1;
      val = Math.sin(pPos * Math.PI) * 0.15;
    }
    // PR segment
    else if (cyclePos >= 0.2 && cyclePos < 0.26) {
      val = 0;
    }
    // QRS complex (Ventricular depolarization)
    else if (cyclePos >= 0.26 && cyclePos < 0.28) {
      // Q wave (small negative)
      val = -0.15;
    } else if (cyclePos >= 0.28 && cyclePos < 0.32) {
      // R wave (sharp positive spike)
      val = 0.95;
    } else if (cyclePos >= 0.32 && cyclePos < 0.35) {
      // S wave (negative dip)
      val = -0.3;
    }
    // ST segment
    else if (cyclePos >= 0.35 && cyclePos < 0.44) {
      val = 0.02;
    }
    // T-wave (Ventricular repolarization)
    else if (cyclePos >= 0.44 && cyclePos < 0.6) {
      const tPos = (cyclePos - 0.44) / 0.16;
      val = Math.sin(tPos * Math.PI) * 0.28;
    }
    // Baseline till next cycle
    else {
      val = (Math.random() - 0.5) * 0.02; // Slight baseline physiological noise
    }

    return val;
  }

  animate() {
    if (!this.ctx) return;
    const ctx = this.ctx;

    // Calculate time relative to current BPM
    const secondsPerBeat = 60 / this.bpm;
    const pixelsPerBeat = 120; // width of one beat at nominal speed
    
    // Clear a trailing scan-bar ahead of the current x position
    const clearWidth = 24;
    ctx.fillStyle = "rgba(2, 6, 23, 0.25)";
    ctx.fillRect(this.x, 0, clearWidth, this.height);

    // Compute waveform sample
    const cycleProgress = (this.x / pixelsPerBeat) % 1.0;
    const signal = this.getEcgSample(cycleProgress);
    const currentY = this.baselineY - (signal * (this.height * 0.42));

    // Draw phosphor glow trace
    ctx.shadowBlur = 10;
    ctx.shadowColor = this.glowColor;
    ctx.strokeStyle = this.traceColor;
    ctx.lineWidth = 2.2;
    ctx.lineCap = "round";

    ctx.beginPath();
    ctx.moveTo(this.x, this.prevY);
    ctx.lineTo(this.x + this.speed, currentY);
    ctx.stroke();

    // Reset shadow for performance
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
