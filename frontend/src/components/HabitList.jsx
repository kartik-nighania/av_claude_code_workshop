import HabitItem from "./HabitItem.jsx";

export default function HabitList({ habits, state, onToggle }) {
  if (habits.length === 0) {
    return <p className="muted">No habits configured.</p>;
  }

  return (
    <ul className="habit-list">
      {habits.map((habit) => (
        <HabitItem
          key={habit.key}
          habit={habit}
          done={Boolean(state[habit.key])}
          onToggle={onToggle}
        />
      ))}
    </ul>
  );
}
