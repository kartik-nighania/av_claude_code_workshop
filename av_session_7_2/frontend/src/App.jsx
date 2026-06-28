import { useEffect, useState } from "react";
import { api } from "./api.js";

const STATUSES = ["pending", "paid", "shipped", "delivered", "cancelled"];

export default function App() {
  const [tab, setTab] = useState("orders");
  const [orders, setOrders] = useState([]);
  const [products, setProducts] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [health, setHealth] = useState(null);
  const [error, setError] = useState(null);

  async function refresh() {
    try {
      const [o, p, c, h] = await Promise.all([
        api.listOrders(),
        api.listProducts(),
        api.listCustomers(),
        api.health(),
      ]);
      setOrders(o);
      setProducts(p);
      setCustomers(c);
      setHealth(h);
      setError(null);
    } catch (e) {
      setError(e.message);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function changeStatus(id, status) {
    try {
      await api.updateOrderStatus(id, status);
      await refresh();
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <div className="app">
      <header>
        <h1>OrderTrack</h1>
        <span className={`badge ${health?.status === "ok" ? "ok" : "bad"}`}>
          {health ? `db:${health.db} · redis:${health.redis}` : "connecting…"}
        </span>
      </header>

      {error && <div className="error">{error}</div>}

      <nav className="tabs">
        {["orders", "products", "customers", "new order"].map((t) => (
          <button
            key={t}
            className={tab === t ? "active" : ""}
            onClick={() => setTab(t)}
          >
            {t}
          </button>
        ))}
      </nav>

      {tab === "orders" && (
        <Orders orders={orders} onChangeStatus={changeStatus} />
      )}
      {tab === "products" && <Products products={products} />}
      {tab === "customers" && <Customers customers={customers} />}
      {tab === "new order" && (
        <NewOrder
          products={products}
          customers={customers}
          onCreated={() => {
            setTab("orders");
            refresh();
          }}
          onError={setError}
        />
      )}
    </div>
  );
}

function Orders({ orders, onChangeStatus }) {
  if (!orders.length) return <p className="muted">No orders yet.</p>;
  return (
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Customer</th>
          <th>Items</th>
          <th>Total</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        {orders.map((o) => (
          <tr key={o.id}>
            <td>{o.id}</td>
            <td>{o.customer_id}</td>
            <td>{o.items.length}</td>
            <td>${o.total.toFixed(2)}</td>
            <td>
              <select
                value={o.status}
                onChange={(e) => onChangeStatus(o.id, e.target.value)}
              >
                {STATUSES.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function Products({ products }) {
  return (
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Name</th>
          <th>SKU</th>
          <th>Price</th>
          <th>Stock</th>
        </tr>
      </thead>
      <tbody>
        {products.map((p) => (
          <tr key={p.id}>
            <td>{p.id}</td>
            <td>{p.name}</td>
            <td>{p.sku}</td>
            <td>${p.price.toFixed(2)}</td>
            <td>{p.stock}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function Customers({ customers }) {
  return (
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Name</th>
          <th>Email</th>
        </tr>
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
  );
}

function NewOrder({ products, customers, onCreated, onError }) {
  const [customerId, setCustomerId] = useState("");
  const [productId, setProductId] = useState("");
  const [quantity, setQuantity] = useState(1);

  async function submit(e) {
    e.preventDefault();
    try {
      await api.createOrder({
        customer_id: Number(customerId),
        items: [{ product_id: Number(productId), quantity: Number(quantity) }],
      });
      onCreated();
    } catch (err) {
      onError(err.message);
    }
  }

  return (
    <form className="new-order" onSubmit={submit}>
      <label>
        Customer
        <select
          value={customerId}
          onChange={(e) => setCustomerId(e.target.value)}
          required
        >
          <option value="">Select…</option>
          {customers.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        Product
        <select
          value={productId}
          onChange={(e) => setProductId(e.target.value)}
          required
        >
          <option value="">Select…</option>
          {products.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name} (${p.price.toFixed(2)})
            </option>
          ))}
        </select>
      </label>
      <label>
        Quantity
        <input
          type="number"
          min="1"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
        />
      </label>
      <button type="submit">Create order</button>
    </form>
  );
}
