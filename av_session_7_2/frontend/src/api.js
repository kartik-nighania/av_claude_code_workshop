// Thin fetch wrapper around the OrderTrack API (proxied to :8010 via Vite).
const BASE = "/api";

async function req(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.error || `Request failed: ${res.status}`);
  }
  return res.json();
}

export const api = {
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
