import { useEffect, useState } from "react";
import { api } from "./api.js";
import AddTodo from "./components/AddTodo.jsx";
import TodoList from "./components/TodoList.jsx";

export default function App() {
  const [todos, setTodos] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  async function refresh() {
    try {
      setTodos(await api.list());
      setError(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handleAdd(title) {
    try {
      await api.create(title);
      await refresh();
    } catch (e) {
      setError(e.message);
    }
  }

  async function handleToggle(id) {
    try {
      await api.toggle(id);
      await refresh();
    } catch (e) {
      setError(e.message);
    }
  }

  async function handleRemove(id) {
    try {
      await api.remove(id);
      await refresh();
    } catch (e) {
      setError(e.message);
    }
  }

  const remaining = todos.filter((t) => !t.completed).length;

  return (
    <main className="app">
      <header>
        <h1>TODO</h1>
        <p className="subtitle">Multi-agent lab — base structure</p>
      </header>

      <AddTodo onAdd={handleAdd} />

      {error && <p className="error">{error}</p>}

      {loading ? (
        <p className="muted">Loading…</p>
      ) : (
        <>
          <TodoList todos={todos} onToggle={handleToggle} onRemove={handleRemove} />
          <footer className="count">
            {remaining} of {todos.length} remaining
          </footer>
        </>
      )}
    </main>
  );
}
