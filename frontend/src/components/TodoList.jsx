import TodoItem from "./TodoItem.jsx";

export default function TodoList({ todos, onToggle, onRemove }) {
  if (todos.length === 0) {
    return <p className="muted">Nothing here yet. Add your first todo above.</p>;
  }

  return (
    <ul className="todo-list">
      {todos.map((todo) => (
        <TodoItem key={todo.id} todo={todo} onToggle={onToggle} onRemove={onRemove} />
      ))}
    </ul>
  );
}
