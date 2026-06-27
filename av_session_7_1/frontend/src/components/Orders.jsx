import React, { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Orders() {
  const [orders, setOrders] = useState([]);
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");

  async function load() {
    setError("");
    try {
      setOrders(await api.orders());
    } catch (err) {
      setError(`Failed to load orders (HTTP ${err.status || "?"})`);
    }
  }

  async function doSearch(e) {
    e.preventDefault();
    setError("");
    try {
      const rows = await api.searchOrders(search);
      setOrders(rows.map((r) => ({ id: r[0], customer_name: r[2], product_id: r[3], quantity: r[4], status: r[5] })));
    } catch (err) {
      setError(`Search failed (HTTP ${err.status || "?"})`);
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <section>
      <div className="row">
        <h2>Orders</h2>
        <form onSubmit={doSearch} className="search">
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by customer name"
          />
          <button type="submit">Search</button>
          <button type="button" onClick={load}>Reset</button>
        </form>
      </div>
      {error && <p className="error">{error}</p>}
      <table>
        <thead>
          <tr><th>ID</th><th>Customer</th><th>Product</th><th>Qty</th><th>Status</th></tr>
        </thead>
        <tbody>
          {orders.map((o) => (
            <tr key={o.id}>
              <td>{o.id}</td>
              <td>{o.customer_name}</td>
              <td>{o.product_id}</td>
              <td>{o.quantity}</td>
              <td>{o.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
