export default function TodoItem({ todo, onToggle, onRemove }) {
  return (
    <li className={`todo-item ${todo.completed ? "done" : ""}`}>
      <label>
        <input
          type="checkbox"
          checked={todo.completed}
          onChange={() => onToggle(todo.id)}
        />
        <span>{todo.title}</span>
      </label>
      <button
        className="remove"
        onClick={() => onRemove(todo.id)}
        aria-label={`Delete ${todo.title}`}
      >
        ✕
      </button>
    </li>
  );
}
