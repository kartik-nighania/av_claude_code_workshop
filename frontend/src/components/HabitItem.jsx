export default function HabitItem({ habit, done, onToggle }) {
  return (
    <li className={`habit-item ${done ? "done" : ""}`}>
      <label>
        <input
          type="checkbox"
          checked={done}
          onChange={() => onToggle(habit.key, !done)}
        />
        <span>{habit.label}</span>
      </label>
    </li>
  );
}
