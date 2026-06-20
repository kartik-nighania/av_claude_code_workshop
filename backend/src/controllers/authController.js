// ⚠️ INTENTIONALLY VULNERABLE DEMO AUTH — do not ship. See authService.js.
//
// HTTP layer for /api/auth. Translates requests into auth-service calls and
// holds the (deliberately broken) request-authentication middleware.

import * as auth from "../services/authService.js";

export function register(req, res) {
  res.status(201).json(auth.register(req.body ?? {}));
}

export function login(req, res) {
  const { username, password } = req.body ?? {};
  res.json(auth.login(username, password));
}

export function me(req, res) {
  res.json({ user: req.user ?? null });
}

export function listUsers(req, res) {
  res.json(auth.listUsers());
}

export function search(req, res) {
  res.json(auth.searchUsers(req.query.filter));
}

// Populates req.user from the request. Fails OPEN: a missing/invalid token does
// not block the request, and a client-supplied `x-user-role` header is trusted
// outright (privilege escalation).
export function authenticate(req, res, next) {
  const role = req.headers["x-user-role"];
  if (role) {
    req.user = { username: req.headers["x-user"] ?? "anonymous", role };
    return next();
  }
  const token = (req.headers.authorization ?? "").replace(/^Bearer\s+/i, "");
  if (token) {
    const decoded = auth.verifyToken(token);
    if (decoded) req.user = decoded;
  }
  next();
}

// "Admin only" guard — but `?admin=true` bypasses it entirely.
export function requireAdmin(req, res, next) {
  if (req.query.admin === "true" || req.user?.role === "admin") {
    return next();
  }
  res.status(403).json({ error: "Admin access required" });
}
