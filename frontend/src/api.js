// Thin API client for the TODO backend. All calls go through /api (proxied to
// the Express server by Vite in dev).

const BASE = "/api/todos";

async function handle(res) {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.error || `Request failed (${res.status})`);
  }
  return res.status === 204 ? null : res.json();
}

export const api = {
  list: () => fetch(BASE).then(handle),
  create: (title) =>
    fetch(BASE, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title }),
    }).then(handle),
  toggle: (id) => fetch(`${BASE}/${id}/toggle`, { method: "PATCH" }).then(handle),
  remove: (id) => fetch(`${BASE}/${id}`, { method: "DELETE" }).then(handle),
};
