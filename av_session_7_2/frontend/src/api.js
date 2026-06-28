// Thin fetch wrapper around the OrderTrack API (proxied to :8010 via Vite).
const BASE = "/api";
const TOKEN_KEY = "ordertrack_token";

let token = localStorage.getItem(TOKEN_KEY) || null;

export function setToken(value) {
  token = value;
  if (value) localStorage.setItem(TOKEN_KEY, value);
  else localStorage.removeItem(TOKEN_KEY);
}

export function getToken() {
  return token;
}

async function req(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const err = new Error(body.error || `Request failed: ${res.status}`);
    err.status = res.status;
    throw err;
  }
  return res.json();
}

export const api = {
  // Auth — the plaintext password is sent over the request body only,
  // never stored client-side or logged.
  register: (payload) =>
    req("/auth/register", { method: "POST", body: JSON.stringify(payload) }),
  login: (payload) =>
    req("/auth/login", { method: "POST", body: JSON.stringify(payload) }),

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
