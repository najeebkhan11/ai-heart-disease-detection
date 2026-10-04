/**
 * CardioAI API Client
 * Manages JWT session tokens and communication with FastAPI backend endpoints.
 */

const API = {
  baseUrl: window.location.origin,

  getToken() {
    return localStorage.getItem("cardio_token");
  },

  setToken(token) {
    if (token) {
      localStorage.setItem("cardio_token", token);
    } else {
      localStorage.removeItem("cardio_token");
    }
  },

  getUser() {
    const raw = localStorage.getItem("cardio_user");
    return raw ? JSON.parse(raw) : null;
  },

  setUser(user) {
    if (user) {
      localStorage.setItem("cardio_user", JSON.stringify(user));
    } else {
      localStorage.removeItem("cardio_user");
    }
  },

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      "Content-Type": "application/json",
      ...(options.headers || {})
    };

    const token = this.getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers
      });

      if (response.status === 401) {
        // Token expired or invalid
        if (token) {
          this.setToken(null);
          this.setUser(null);
          window.dispatchEvent(new CustomEvent("cardio:auth_changed"));
        }
      }

      const data = await response.json();
      if (!response.ok) {
        const errorMsg = data.detail || (Array.isArray(data.detail) ? data.detail[0]?.msg : "An error occurred");
        throw new Error(errorMsg);
      }
      return data;
    } catch (err) {
      console.error(`API Error on [${options.method || "GET"} ${endpoint}]:`, err);
      throw err;
    }
  },

  // Auth Endpoints
  async register(username, password, fullName = "") {
    const data = await this.request("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ username, password, full_name: fullName })
    });
    this.setToken(data.access_token);
    this.setUser(data.user);
    window.dispatchEvent(new CustomEvent("cardio:auth_changed"));
    return data;
  },

  async login(username, password) {
    const data = await this.request("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password })
    });
    this.setToken(data.access_token);
    this.setUser(data.user);
    window.dispatchEvent(new CustomEvent("cardio:auth_changed"));
    return data;
  },

  logout() {
    this.setToken(null);
    this.setUser(null);
    window.dispatchEvent(new CustomEvent("cardio:auth_changed"));
  },

  async getProfile() {
    return await this.request("/api/auth/me");
  },

  // Prediction & Analytics
  async predict(patientData) {
    return await this.request("/api/predict", {
      method: "POST",
      body: JSON.stringify(patientData)
    });
  },

  async getStats() {
    return await this.request("/api/stats");
  },

  // History Endpoints
  async getHistory() {
    return await this.request("/api/history");
  },

  async deleteHistoryItem(id) {
    return await this.request(`/api/history/${id}`, {
      method: "DELETE"
    });
  },

  async clearHistory() {
    return await this.request("/api/history", {
      method: "DELETE"
    });
  },

  // Live Sensors
  async getLiveSensors() {
    return await this.request("/api/sensors/live");
  }
};
