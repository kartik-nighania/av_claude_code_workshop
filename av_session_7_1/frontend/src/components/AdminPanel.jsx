import React, { useState } from "react";
import { api } from "../api.js";

export default function AdminPanel() {
  const [users, setUsers] = useState(null);
  const [error, setError] = useState("");

  async function load() {
    setError("");
    try {
      setUsers(await api.adminUsers());
    } catch (err) {
      setError(`Failed (HTTP ${err.status || "?"})`);
    }
  }

  return (
    <section>
      <h2>Admin</h2>
      <p className="warn">
        This calls <code>/api/admin/users</code> with no token — it should require
        auth, but currently does not.
      </p>
      <button onClick={load}>Load admin users</button>
      {error && <p className="error">{error}</p>}
      {users && <pre>{JSON.stringify(users, null, 2)}</pre>}
    </section>
  );
}
