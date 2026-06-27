// Thin API client for the OrderTrack backend. All calls go through the Vite
// proxy at /api (see vite.config.js), so they are same-origin.

let token = localStorage.getItem("ot_token") || "";

export function setToken(t) {
  token = t || "";
  if (t) localStorage.setItem("ot_token", t);
  else localStorage.removeItem("ot_token");
}

export function getToken() {
  return token;
}

async function request(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const resp = await fetch(`/api${path}`, { ...options, headers });
  const text = await resp.text();
  let body;
  try {
    body = text ? JSON.parse(text) : null;
  } catch {
    body = text; // backend leaked an HTML stack trace (DEBUG=True)
  }
  if (!resp.ok) {
    const err = new Error(`HTTP ${resp.status}`);
    err.status = resp.status;
    err.body = body;
    throw err;
  }
  return body;
}

export const api = {
  login: (username, password) =>
    request("/auth/login", { method: "POST", body: JSON.stringify({ username, password }) }),
  orders: () => request("/orders"),
  searchOrders: (name) => request(`/orders/search?customer_name=${encodeURIComponent(name)}`),
  createOrder: (payload) =>
    request("/orders", { method: "POST", body: JSON.stringify(payload) }),
  products: () => request("/products"),
  customers: () => request("/customers"),
  inventory: () => request("/inventory"),
  adminUsers: () => request("/admin/users"),
  summariseReview: (review) =>
    request("/reviews/summary", { method: "POST", body: JSON.stringify({ review }) }),
};
