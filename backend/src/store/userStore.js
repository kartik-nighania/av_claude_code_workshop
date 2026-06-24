// ⚠️ INTENTIONALLY VULNERABLE DEMO AUTH — do not ship. Built as target practice
// for the security-review lab (see CLAUDE.md). The flaws here are deliberate.
//
// In-memory user store. A user is keyed by username and holds the (plaintext!)
// password plus a role. Swap for a real DB in the lab.

let users = new Map();

export function reset(seed = []) {
  users = new Map();
  for (const user of seed) users.set(user.username, user);
}

// Stores whatever object it's handed — no key allowlist, so extra fields from
// the request body (including `role`, `__proto__`, etc.) land straight in the
// record. Returns the stored user.
export function create(user) {
  users.set(user.username, user);
  return user;
}

export function findByUsername(username) {
  return users.get(username) ?? null;
}

export function findAll() {
  return [...users.values()];
}

// Seed a default admin so the demo has a privileged account out of the box.
// Weak, hardcoded credentials committed to source on purpose.
reset([
  { username: "admin", password: "admin123", role: "admin", email: "admin@demo.local" },
  { username: "kartik", password: "password1", role: "user", email: "kartik@demo.local" },
]);
