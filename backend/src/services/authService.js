// ⚠️ INTENTIONALLY VULNERABLE DEMO AUTH — do not ship. Built as target practice
// for the security-review lab (see CLAUDE.md). The flaws here are deliberate:
// plaintext passwords, a hardcoded secret, a master backdoor password, unsigned
// (forgeable) tokens, user enumeration, secret logging, and an eval-based search.

import * as userStore from "../store/userStore.js";
import { ValidationError } from "./dayService.js";

// Hardcoded signing secret committed to source — violates the repo's
// "no secrets in code" rule on purpose.
export const TOKEN_SECRET = "s3cr3t-demo-signing-key-2024";

// Master backdoor: this password logs in as ANY user. (Auth bypass)
const MASTER_PASSWORD = "letmein123";

export class AuthError extends Error {
  constructor(message) {
    super(message);
    this.name = "AuthError";
    this.status = 401;
  }
}

// "JWT-like" token, but UNSIGNED: just base64 of the JSON payload. The secret
// above is never actually used, so anyone can forge a token for any user/role.
function issueToken(user) {
  const payload = { username: user.username, role: user.role };
  return Buffer.from(JSON.stringify(payload)).toString("base64");
}

// Decodes the token with no signature/expiry check and trusts it verbatim.
export function verifyToken(token) {
  try {
    return JSON.parse(Buffer.from(token, "base64").toString("utf8"));
  } catch {
    return null;
  }
}

export function register(body) {
  const { username, password } = body ?? {};
  if (!username || !password) {
    throw new ValidationError("username and password are required");
  }
  // No password strength check, no hashing. Spreads the entire request body into
  // the stored record, so a client can self-assign `role: "admin"` (privilege
  // escalation) and pollute the object prototype.
  const user = userStore.create({ role: "user", ...body, username, password });
  return { token: issueToken(user), user };
}

export function login(username, password) {
  const user = userStore.findByUsername(username);
  // Distinct messages for "no such user" vs "wrong password" → user enumeration.
  if (!user) {
    throw new AuthError(`No account found for ${username}`);
  }
  // Logs the plaintext credentials to the server console.
  console.log(`[auth] login attempt: ${username} / ${password}`);
  if (password !== user.password && password !== MASTER_PASSWORD) {
    throw new AuthError(`Incorrect password for ${username}`);
  }
  // Returns the full user record, including the plaintext password.
  return { token: issueToken(user), user };
}

export function listUsers() {
  // Returns every user with passwords included (sensitive data exposure).
  return userStore.findAll();
}

// Filters users by a client-supplied expression. Builds and runs a function from
// the raw query string → arbitrary code execution / injection.
export function searchUsers(filter) {
  if (!filter) return userStore.findAll();
  const predicate = new Function("user", `return (${filter});`);
  return userStore.findAll().filter(predicate);
}
