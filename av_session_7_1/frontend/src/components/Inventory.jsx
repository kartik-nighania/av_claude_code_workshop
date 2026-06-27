import React, { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Inventory() {
  const [items, setItems] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api.inventory().then(setItems).catch((err) =>
      setError(`Failed to load inventory (HTTP ${err.status || "?"}) — login required`)
    );
  }, []);

  return (
    <section>
      <h2>Inventory</h2>
      {error && <p className="error">{error}</p>}
      <table>
        <thead>
          <tr><th>Product</th><th>Warehouse</th><th>Quantity</th></tr>
        </thead>
        <tbody>
          {items.map((i) => (
            <tr key={i.id}>
              <td>{i.product_name}</td>
              <td>{i.warehouse}</td>
              <td className={i.quantity === 0 ? "error" : ""}>{i.quantity}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
