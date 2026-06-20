import { useEffect, useState } from "react";
import { api } from "./api.js";
import DaySelector from "./components/DaySelector.jsx";
import HabitList from "./components/HabitList.jsx";

// Local YYYY-MM-DD for "today" (avoids UTC drift from toISOString).
function todayISO() {
  const now = new Date();
  const offset = now.getTimezoneOffset() * 60000;
  return new Date(now.getTime() - offset).toISOString().slice(0, 10);
}

export default function App() {
  const [habits, setHabits] = useState([]);
  const [date, setDate] = useState(todayISO);
  const [state, setState] = useState({});
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  // Load the fixed habit definitions once.
  useEffect(() => {
    api
      .habits()
      .then(setHabits)
      .catch((e) => setError(e.message));
  }, []);

  // Load the selected day's habit state whenever the date changes.
  useEffect(() => {
    let active = true;
    setLoading(true);
    api
      .getDay(date)
      .then((day) => {
        if (!active) return;
        setState(day.habits);
        setError(null);
      })
      .catch((e) => active && setError(e.message))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [date]);

  async function handleToggle(key, value) {
    // Optimistic update, reconciled with the server response.
    setState((prev) => ({ ...prev, [key]: value }));
    try {
      const day = await api.updateDay(date, { [key]: value });
      setState(day.habits);
      setError(null);
    } catch (e) {
      setError(e.message);
      // Roll back on failure.
      setState((prev) => ({ ...prev, [key]: !value }));
    }
  }

  const done = Object.values(state).filter(Boolean).length;
  const total = habits.length;
  const allDone = total > 0 && done === total;

  return (
    <main className="app">
      <header>
        <h1>Health Tracker</h1>
        <p className="subtitle">Daily habits — one day at a time</p>
      </header>

      <DaySelector date={date} onChange={setDate} />

      {error && <p className="error">{error}</p>}

      {loading ? (
        <p className="muted">Loading…</p>
      ) : (
        <>
          <HabitList habits={habits} state={state} onToggle={handleToggle} />
          <footer className="count">
            {allDone ? "All habits done — nice! 🎉" : `${done} of ${total} habits done`}
          </footer>
        </>
      )}
    </main>
  );
}
