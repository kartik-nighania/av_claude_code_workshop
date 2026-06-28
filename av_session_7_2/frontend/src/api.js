// Thin fetch wrapper around the OrderTrack API (proxied to :8010 via Vite).
const BASE = "/api";
const TOKEN_KEY = "ordertrack_token";

// --- token storage (localStorage) -----------------------------------------
export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}
export function setToken(token) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

async function req(path, options = {}, { base = BASE } = {}) {
  const token = getToken();
  const res = await fetch(`${base}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const err = new Error(body.error || `Request failed: ${res.status}`);
    err.status = res.status;
    throw err;
  }
  return res.json();
}

export const api = {
  // auth (mounted at /auth, not /api)
  register: (email, password) =>
    req("/register", { method: "POST", body: JSON.stringify({ email, password }) }, { base: "/auth" }),
  login: (email, password) =>
    req("/login", { method: "POST", body: JSON.stringify({ email, password }) }, { base: "/auth" }),

  health: () => req("/health"),
  listOrders: () => req("/orders"),
  listProducts: () => req("/products"),
  listCustomers: () => req("/customers"),
  orderStatus: (id) => req(`/orders/${id}/status`),
  createOrder: (payload) =>
    req("/orders", { method: "POST", body: JSON.stringify(payload) }),
  updateOrderStatus: (id, status) =>
    req(`/orders/${id}`, { method: "PUT", body: JSON.stringify({ status }) }),
};
