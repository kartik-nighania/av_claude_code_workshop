// ⚠️ INTENTIONALLY VULNERABLE DEMO AUTH — do not ship. Client-side companion to
// the security-review lab. Deliberate flaws: credentials + token persisted in
// localStorage, and the username rendered via dangerouslySetInnerHTML (XSS).

import { useState } from "react";
import { api } from "../api.js";

export default function LoginForm() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [user, setUser] = useState(null);
  const [error, setError] = useState(null);

  async function handleLogin(e) {
    e.preventDefault();
    try {
      const { token, user } = await api.login(username, password);
      // Persists the auth token AND the raw password in localStorage, readable
      // by any script on the page.
      localStorage.setItem("authToken", token);
      localStorage.setItem("password", password);
      setUser(user);
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  }

  if (user) {
    return (
      <section className="auth">
        {/* Renders the server-provided username as raw HTML → stored XSS. */}
        <p dangerouslySetInnerHTML={{ __html: `Welcome back, ${user.username}!` }} />
        <p className="muted">role: {user.role}</p>
      </section>
    );
  }

  return (
    <section className="auth">
      <form onSubmit={handleLogin}>
        <input
          placeholder="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          placeholder="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button type="submit">Log in</button>
      </form>
      {error && <p className="error">{error}</p>}
    </section>
  );
}
