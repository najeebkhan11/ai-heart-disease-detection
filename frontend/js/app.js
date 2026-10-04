/**
 * CardioAI Main Application Controller
 */

document.addEventListener("DOMContentLoaded", () => {
  // App State
  let currentUser = API.getUser();
  let ecgMonitor = null;
  let telemetryInterval = null;
  let lastAssessmentData = null;

  // Patient Sample Presets
  const PRESETS = {
    normal: {
      age: 38,
      sex: 0, // Female
      cp: 2,  // Non-anginal pain
      trestbps: 118,
      chol: 175,
      fbs: 0,
      restecg: 0,
      thalach: 175,
      exang: 0,
      oldpeak: 0.2,
      slope: 2, // Downsloping/Upsloping
      ca: 0,
      thal: 0  // Normal
    },
    highRisk: {
      age: 63,
      sex: 1, // Male
      cp: 0,  // Typical angina
      trestbps: 155,
      chol: 285,
      fbs: 1,
      restecg: 1,
      thalach: 118,
      exang: 1, // Yes
      oldpeak: 2.8,
      slope: 1, // Flat
      ca: 2,
      thal: 2  // Reversible defect
    },
    default: {
      age: 52,
      sex: 1,
      cp: 1,
      trestbps: 125,
      chol: 212,
      fbs: 0,
      restecg: 0,
      thalach: 168,
      exang: 0,
      oldpeak: 1.0,
      slope: 2,
      ca: 0,
      thal: 2
    }
  };

  // Initialize ECG Visualizer
  if (document.getElementById("ecgCanvas")) {
    ecgMonitor = new ECGVisualizer("ecgCanvas");
  }

  // UI Element References
  const form = document.getElementById("assessmentForm");
  const authModal = document.getElementById("authModal");
  const authBtn = document.getElementById("authBtn");
  const userProfileBadge = document.getElementById("userProfileBadge");
  const usernameDisplay = document.getElementById("usernameDisplay");
  const logoutBtn = document.getElementById("logoutBtn");
  const toastContainer = document.getElementById("toastContainer");

  // --- Toast Notifications ---
  function showToast(message, type = "info") {
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    const icon = type === "success" ? "✅" : (type === "error" ? "⚠️" : "ℹ️");
    toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
    toastContainer.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateX(100%)";
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }

  // --- Auth UI Handling ---
  function updateAuthUI() {
    currentUser = API.getUser();
    if (currentUser && currentUser.username) {
      authBtn.style.display = "none";
      userProfileBadge.style.display = "flex";
      usernameDisplay.textContent = currentUser.full_name || currentUser.username;
      loadHistory();
      loadUserStats();
    } else {
      authBtn.style.display = "inline-flex";
      userProfileBadge.style.display = "none";
      usernameDisplay.textContent = "";
    }
  }

  window.addEventListener("cardio:auth_changed", updateAuthUI);
  updateAuthUI();

  // Open Auth Modal
  if (authBtn) {
    authBtn.addEventListener("click", () => {
      authModal.classList.add("active");
    });
  }

  // Close Modal on backdrop click or close button
  document.querySelectorAll(".modal-close, .modal-overlay").forEach(el => {
    el.addEventListener("click", (e) => {
      if (e.target === el) {
        authModal.classList.remove("active");
      }
    });
  });

  // Modal Auth Tabs
  const loginTabBtn = document.getElementById("tabLoginBtn");
  const registerTabBtn = document.getElementById("tabRegisterBtn");
  const loginForm = document.getElementById("loginForm");
  const registerForm = document.getElementById("registerForm");

  loginTabBtn.addEventListener("click", () => {
    loginTabBtn.classList.add("active");
    registerTabBtn.classList.remove("active");
    loginForm.style.display = "flex";
    registerForm.style.display = "none";
  });

  registerTabBtn.addEventListener("click", () => {
    registerTabBtn.classList.add("active");
    loginTabBtn.classList.remove("active");
    registerForm.style.display = "flex";
    loginForm.style.display = "none";
  });

  // Handle Login Submit
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const u = document.getElementById("loginUsername").value.trim();
    const p = document.getElementById("loginPassword").value;
    const submitBtn = loginForm.querySelector("button[type='submit']");

    try {
      submitBtn.disabled = true;
      submitBtn.textContent = "Authenticating...";
      await API.login(u, p);
      authModal.classList.remove("active");
      loginForm.reset();
      showToast(`Welcome back, ${u}!`, "success");
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Sign In";
    }
  });

  // Handle Register Submit
  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const u = document.getElementById("regUsername").value.trim();
    const fn = document.getElementById("regFullName").value.trim();
    const p = document.getElementById("regPassword").value;
    const submitBtn = registerForm.querySelector("button[type='submit']");

    try {
      submitBtn.disabled = true;
      submitBtn.textContent = "Creating Account...";
      await API.register(u, p, fn);
      authModal.classList.remove("active");
      registerForm.reset();
      showToast(`Account created successfully! Welcome, ${u}!`, "success");
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Create Account";
    }
  });

  // Handle Logout
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      API.logout();
      showToast("Signed out successfully.", "info");
    });
  }

  // --- Navigation Tabs ---
  const navButtons = document.querySelectorAll(".nav-btn");
  const sections = document.querySelectorAll(".page-section");

  navButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const target = btn.getAttribute("data-tab");
      navButtons.forEach(b => b.classList.remove("active"));
      sections.forEach(s => s.classList.remove("active"));
      
      btn.classList.add("active");
      const targetSection = document.getElementById(`section-${target}`);
      if (targetSection) {
        targetSection.classList.add("active");
      }

      if (target === "history" && API.getToken()) {
        loadHistory();
      }
    });
  });

  // --- Sliders and Value Display Sync ---
  function setupSliderSync(id, displayId, unit = "") {
    const slider = document.getElementById(id);
    const display = document.getElementById(displayId);
    if (!slider || !display) return;

    slider.addEventListener("input", () => {
      display.textContent = `${slider.value}${unit ? " " + unit : ""}`;
    });
  }

  setupSliderSync("input_age", "val_age", "yrs");
  setupSliderSync("input_trestbps", "val_trestbps", "mm Hg");
  setupSliderSync("input_chol", "val_chol", "mg/dl");
  setupSliderSync("input_thalach", "val_thalach", "bpm");
  setupSliderSync("input_oldpeak", "val_oldpeak", "mm");

  // Update ECG when thalach changes
  const thalachSlider = document.getElementById("input_thalach");
  if (thalachSlider && ecgMonitor) {
    thalachSlider.addEventListener("input", () => {
      ecgMonitor.setBpm(parseInt(thalachSlider.value, 10));
    });
  }

  // --- Populate Form with Preset Values ---
  function applyPreset(preset) {
    document.getElementById("input_age").value = preset.age;
    document.getElementById("val_age").textContent = `${preset.age} yrs`;

    document.getElementById("input_sex").value = preset.sex;
    document.getElementById("input_cp").value = preset.cp;

    document.getElementById("input_trestbps").value = preset.trestbps;
    document.getElementById("val_trestbps").textContent = `${preset.trestbps} mm Hg`;

    document.getElementById("input_chol").value = preset.chol;
    document.getElementById("val_chol").textContent = `${preset.chol} mg/dl`;

    document.getElementById("input_fbs").value = preset.fbs;
    document.getElementById("input_restecg").value = preset.restecg;

    document.getElementById("input_thalach").value = preset.thalach;
    document.getElementById("val_thalach").textContent = `${preset.thalach} bpm`;
    if (ecgMonitor) ecgMonitor.setBpm(preset.thalach);

    document.getElementById("input_exang").value = preset.exang;

    document.getElementById("input_oldpeak").value = preset.oldpeak;
    document.getElementById("val_oldpeak").textContent = `${preset.oldpeak} mm`;

    document.getElementById("input_slope").value = preset.slope;
    document.getElementById("input_ca").value = preset.ca;
    document.getElementById("input_thal").value = preset.thal;
  }

  document.getElementById("presetNormalBtn")?.addEventListener("click", () => {
    applyPreset(PRESETS.normal);
    showToast("Loaded Normal Patient profile", "info");
  });

  document.getElementById("presetHighRiskBtn")?.addEventListener("click", () => {
    applyPreset(PRESETS.highRisk);
    showToast("Loaded High Risk Patient profile", "info");
  });

  document.getElementById("presetResetBtn")?.addEventListener("click", () => {
    applyPreset(PRESETS.default);
    showToast("Reset to default clinical inputs", "info");
  });

  // --- Assessment Form Submit ---
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const predictBtn = document.getElementById("predictBtn");

      const patientData = {
        age: parseInt(document.getElementById("input_age").value, 10),
        sex: parseInt(document.getElementById("input_sex").value, 10),
        cp: parseInt(document.getElementById("input_cp").value, 10),
        trestbps: parseInt(document.getElementById("input_trestbps").value, 10),
        chol: parseInt(document.getElementById("input_chol").value, 10),
        fbs: parseInt(document.getElementById("input_fbs").value, 10),
        restecg: parseInt(document.getElementById("input_restecg").value, 10),
        thalach: parseInt(document.getElementById("input_thalach").value, 10),
        exang: parseInt(document.getElementById("input_exang").value, 10),
        oldpeak: parseFloat(document.getElementById("input_oldpeak").value),
        slope: parseInt(document.getElementById("input_slope").value, 10),
        ca: parseInt(document.getElementById("input_ca").value, 10),
        thal: parseInt(document.getElementById("input_thal").value, 10)
      };

      try {
        predictBtn.disabled = true;
        predictBtn.innerHTML = `<span>⏳</span> Analyzing Biomarkers...`;
        
        const result = await API.predict(patientData);
        lastAssessmentData = result;
        renderResults(result);
        showToast("Risk assessment complete!", "success");

        if (API.getToken()) {
          loadHistory();
          loadUserStats();
        }
      } catch (err) {
        showToast(err.message, "error");
      } finally {
        predictBtn.disabled = false;
        predictBtn.innerHTML = `<span>🧠</span> Run AI Cardiac Risk Assessment`;
      }
    });
  }

  // --- Render Results & Animated Risk Gauge ---
  function renderResults(result) {
    const riskScore = result.risk_score;
    const riskLevel = result.risk_level;

    // Elements
    const numberEl = document.getElementById("riskScoreNumber");
    const badgeEl = document.getElementById("riskLevelBadge");
    const gaugeFill = document.getElementById("gaugeFill");
    const factorsContainer = document.getElementById("riskFactorsContainer");
    const recsContainer = document.getElementById("recommendationsContainer");
    const printBtn = document.getElementById("printReportBtn");

    if (printBtn) printBtn.style.display = "inline-flex";

    // Animated number counter
    let current = 0;
    const duration = 800;
    const stepTime = 15;
    const totalSteps = duration / stepTime;
    const increment = riskScore / totalSteps;
    const timer = setInterval(() => {
      current += increment;
      if (current >= riskScore) {
        current = riskScore;
        clearInterval(timer);
      }
      numberEl.textContent = Math.round(current);
    }, stepTime);

    // Update semi-circle gauge (stroke-dasharray: 283)
    const maxOffset = 283;
    const fillOffset = maxOffset - (maxOffset * (riskScore / 100));
    gaugeFill.style.strokeDashoffset = fillOffset;

    let color = "#10b981"; // green
    if (riskScore > 50) {
      color = "#ef4444"; // red
    } else if (riskScore > 30) {
      color = "#f59e0b"; // amber
    }
    gaugeFill.style.stroke = color;

    // Update Badge
    badgeEl.className = `risk-badge ${riskLevel.toLowerCase()}`;
    const badgeIcon = riskLevel === "High" ? "🚨" : (riskLevel === "Moderate" ? "⚠️" : "✅");
    badgeEl.innerHTML = `${badgeIcon} ${riskLevel} Risk (${riskScore}%)`;

    // Render Risk Factors
    factorsContainer.innerHTML = "";
    if (result.risk_factors && result.risk_factors.length > 0) {
      result.risk_factors.forEach(f => {
        const item = document.createElement("div");
        item.className = "factor-item";
        const icon = f.severity === "high" ? "🔴" : (f.severity === "moderate" ? "🟡" : "🟢");
        item.innerHTML = `
          <div class="factor-icon">${icon}</div>
          <div class="factor-details">
            <div class="factor-header">
              <span>${f.label}</span>
              <span class="factor-val severity-${f.severity}">${f.value}</span>
            </div>
            <div class="factor-msg">${f.message}</div>
          </div>
        `;
        factorsContainer.appendChild(item);
      });
    }

    // Render Recommendations
    recsContainer.innerHTML = "";
    if (result.recommendations && result.recommendations.length > 0) {
      result.recommendations.forEach(r => {
        const item = document.createElement("div");
        item.className = `rec-card priority-${r.priority}`;
        item.innerHTML = `
          <div class="rec-card-title">
            <span>${r.title}</span>
            <span class="rec-badge">${r.category}</span>
          </div>
          <div class="rec-desc">${r.description}</div>
        `;
        recsContainer.appendChild(item);
      });
    }

    // Update Printable Report Meta
    const reportUser = document.getElementById("printReportUser");
    const reportDate = document.getElementById("printReportDate");
    if (reportUser) reportUser.textContent = currentUser ? (currentUser.full_name || currentUser.username) : "Anonymous Patient";
    if (reportDate) reportDate.textContent = result.timestamp;
  }

  // --- Print / Export Report ---
  document.getElementById("printReportBtn")?.addEventListener("click", () => {
    window.print();
  });

  // --- History Management ---
  async function loadHistory() {
    if (!API.getToken()) return;
    const historyBody = document.getElementById("historyTableBody");
    if (!historyBody) return;

    try {
      const items = await API.getHistory();
      if (!items || items.length === 0) {
        historyBody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-muted); padding: 30px;">No assessment records yet. Run a screening to log your data!</td></tr>`;
        return;
      }

      historyBody.innerHTML = items.map(item => {
        const lvlClass = (item.risk_level || "low").toLowerCase();
        const badgeIcon = lvlClass === "high" ? "🚨" : (lvlClass === "moderate" ? "⚠️" : "✅");
        return `
          <tr>
            <td><strong>#${item.id}</strong></td>
            <td>${item.timestamp}</td>
            <td><span class="risk-badge ${lvlClass}" style="margin: 0; padding: 2px 10px; font-size: 0.78rem;">${badgeIcon} ${item.risk_level}</span></td>
            <td><strong style="font-family: var(--font-mono);">${item.risk}%</strong></td>
            <td>
              <button class="btn btn-danger delete-history-btn" data-id="${item.id}" style="padding: 4px 10px; font-size: 0.75rem;">
                Delete
              </button>
            </td>
          </tr>
        `;
      }).join("");

      // Attach delete listeners
      document.querySelectorAll(".delete-history-btn").forEach(btn => {
        btn.addEventListener("click", async () => {
          const id = btn.getAttribute("data-id");
          try {
            await API.deleteHistoryItem(id);
            showToast(`Deleted record #${id}`, "info");
            loadHistory();
            loadUserStats();
          } catch (err) {
            showToast(err.message, "error");
          }
        });
      });
    } catch (err) {
      console.error("Error loading history:", err);
    }
  }

  // Clear All History Button
  document.getElementById("clearHistoryBtn")?.addEventListener("click", async () => {
    if (!confirm("Are you sure you want to permanently clear all your prediction records?")) {
      return;
    }
    try {
      await API.clearHistory();
      showToast("History cleared successfully.", "success");
      loadHistory();
      loadUserStats();
    } catch (err) {
      showToast(err.message, "error");
    }
  });

  // --- User Stats Dashboard ---
  async function loadUserStats() {
    if (!API.getToken()) return;
    try {
      const stats = await API.getStats();
      const countEl = document.getElementById("statTotalTests");
      const avgEl = document.getElementById("statAvgRisk");
      const statusEl = document.getElementById("statLatestStatus");

      if (countEl) countEl.textContent = stats.total_assessments;
      if (avgEl) avgEl.textContent = `${stats.average_risk}%`;
      if (statusEl) {
        if (stats.last_risk !== null) {
          const statusText = stats.last_risk <= 30 ? "Low Risk" : (stats.last_risk <= 50 ? "Moderate" : "Elevated");
          statusEl.textContent = `${statusText} (${stats.last_risk}%)`;
        } else {
          statusEl.textContent = "No Screenings";
        }
      }
    } catch (err) {
      console.error("Error loading stats:", err);
    }
  }

  // --- Live Sensor Telemetry Polling ---
  async function pollSensors() {
    try {
      const data = await API.getLiveSensors();
      const pulseEl = document.getElementById("telemetryPulse");
      const hrEl = document.getElementById("telemetryHR");
      const spo2El = document.getElementById("telemetrySpO2");
      const bpEl = document.getElementById("telemetryBP");

      if (pulseEl) pulseEl.textContent = data.pulse_bpm;
      if (hrEl) hrEl.textContent = data.heart_rate_bpm;
      if (spo2El) spo2El.textContent = data.spo2_percent;
      if (bpEl) bpEl.textContent = `${data.blood_pressure_systolic}/${data.blood_pressure_diastolic}`;

      // Update Live ECG Rhythm
      if (ecgMonitor && !document.hidden) {
        ecgMonitor.setBpm(data.heart_rate_bpm);
      }
    } catch (err) {
      // Graceful fallback if server unavailable
    }
  }

  // Initial poll and recurring every 3.5s
  pollSensors();
  telemetryInterval = setInterval(pollSensors, 3500);

  // --- Theme Toggle ---
  const themeToggle = document.getElementById("themeToggle");
  if (themeToggle) {
    const savedTheme = localStorage.getItem("cardio_theme") || "dark";
    document.documentElement.setAttribute("data-theme", savedTheme);
    themeToggle.textContent = savedTheme === "light" ? "🌙" : "☀️";

    themeToggle.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-theme");
      const next = current === "light" ? "dark" : "light";
      document.documentElement.setAttribute("data-theme", next);
      localStorage.setItem("cardio_theme", next);
      themeToggle.textContent = next === "light" ? "🌙" : "☀️";
    });
  }

  // Initial trigger
  applyPreset(PRESETS.default);
});
