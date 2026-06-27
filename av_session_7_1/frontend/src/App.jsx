import React, { useState } from "react";
import { api, setToken, getToken } from "./api.js";
import Orders from "./components/Orders.jsx";
import Products from "./components/Products.jsx";
import Customers from "./components/Customers.jsx";
import Inventory from "./components/Inventory.jsx";
import AdminPanel from "./components/AdminPanel.jsx";
import Reviews from "./components/Reviews.jsx";

const TABS = ["Orders", "Products", "Customers", "Inventory", "Reviews", "Admin"];

export default function App() {
  const [tab, setTab] = useState("Orders");
  const [authed, setAuthed] = useState(Boolean(getToken()));
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin123");
  const [loginError, setLoginError] = useState("");

  async function handleLogin(e) {
    e.preventDefault();
    setLoginError("");
    try {
      const { token } = await api.login(username, password);
      setToken(token);
      setAuthed(true);
    } catch (err) {
      setLoginError("Login failed");
    }
  }

  function logout() {
    setToken("");
    setAuthed(false);
  }

  return (
    <div className="app">
      <header className="topbar">
        <h1>OrderTrack</h1>
        <span className="subtitle">Python · Flask · PostgreSQL · Redis</span>
        <div className="spacer" />
        {authed ? (
          <button onClick={logout}>Logout</button>
        ) : (
          <form className="login" onSubmit={handleLogin}>
            <input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="user" />
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="password"
            />
            <button type="submit">Login</button>
            {loginError && <span className="error">{loginError}</span>}
          </form>
        )}
      </header>

      <nav className="tabs">
        {TABS.map((t) => (
          <button key={t} className={tab === t ? "active" : ""} onClick={() => setTab(t)}>
            {t}
          </button>
        ))}
      </nav>

      <main className="content">
        {tab === "Orders" && <Orders />}
        {tab === "Products" && <Products />}
        {tab === "Customers" && <Customers />}
        {tab === "Inventory" && <Inventory />}
        {tab === "Reviews" && <Reviews />}
        {tab === "Admin" && <AdminPanel />}
      </main>
    </div>
  );
}
