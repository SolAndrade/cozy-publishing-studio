const config = window.COZY_CONFIG || {};

export const api = {
  get enabled() {
    return Boolean(config.apiBaseUrl);
  },
  async request(path, options = {}) {
    if (!this.enabled) throw new Error("Backend todavía no conectado");
    const response = await fetch(`${config.apiBaseUrl}${path}`, {
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
      ...options,
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(body.error || `HTTP ${response.status}`);
    return body;
  },
  health() { return this.request("/health"); },
  createSeries(payload) {
    return this.request("/api/series", { method: "POST", body: JSON.stringify(payload) });
  }
};
