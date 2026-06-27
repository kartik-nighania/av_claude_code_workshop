import React, { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Products() {
  const [products, setProducts] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api.products().then(setProducts).catch((err) =>
      setError(`Failed to load products (HTTP ${err.status || "?"}) — login required`)
    );
  }, []);

  return (
    <section>
      <h2>Products</h2>
      {error && <p className="error">{error}</p>}
      <table>
        <thead>
          <tr><th>ID</th><th>Name</th><th>SKU</th><th>Price</th></tr>
        </thead>
        <tbody>
          {products.map((p) => (
            <tr key={p.id}>
              <td>{p.id}</td>
              <td>{p.name}</td>
              <td>{p.sku}</td>
              <td>${p.price}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
