// Thin API client for the Health Tracker backend. All calls go through /api
// (proxied to the Express server by Vite in dev).

const BASE = "/api";

async function handle(res) {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.error || `Request failed (${res.status})`);
  }
  return res.status === 204 ? null : res.json();
}

export const api = {
  // The fixed habit definitions ([{ key, label }]).
  habits: () => fetch(`${BASE}/habits`).then(handle),
  // The habit state for a single day; the backend creates a default day if needed.
  getDay: (date) => fetch(`${BASE}/days/${date}`).then(handle),
  // Update one or more habit booleans for a day.
  updateDay: (date, patch) =>
    fetch(`${BASE}/days/${date}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(patch),
    }).then(handle),
  // Full tracked-day history.
  history: () => fetch(`${BASE}/days`).then(handle),

  // ⚠️ INTENTIONALLY VULNERABLE DEMO AUTH — see backend/src/services/authService.js.
  register: (username, password) =>
    fetch(`${BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    }).then(handle),
  login: (username, password) =>
    fetch(`${BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    }).then(handle),
};
