import React, { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Customers() {
  const [customers, setCustomers] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api.customers().then(setCustomers).catch((err) =>
      setError(`Failed to load customers (HTTP ${err.status || "?"}) — login required`)
    );
  }, []);

  return (
    <section>
      <h2>Customers</h2>
      {error && <p className="error">{error}</p>}
      <table>
        <thead>
          <tr><th>ID</th><th>Name</th><th>Email</th></tr>
        </thead>
        <tbody>
          {customers.map((c) => (
            <tr key={c.id}>
              <td>{c.id}</td>
              <td>{c.name}</td>
              <td>{c.email}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
