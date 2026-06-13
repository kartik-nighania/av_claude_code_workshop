// In-memory data store for todos.
// Swap this module for a real DB (Postgres/SQLite) in the lab — the service
// layer only depends on the functions exported here, not on the storage.

let todos = [];
let nextId = 1;

export function reset(seed = []) {
  todos = seed.map((t) => ({ ...t }));
  nextId = todos.reduce((max, t) => Math.max(max, t.id), 0) + 1;
}

export function findAll() {
  return todos.map((t) => ({ ...t }));
}

export function findById(id) {
  const found = todos.find((t) => t.id === id);
  return found ? { ...found } : null;
}

export function insert({ title }) {
  const todo = {
    id: nextId++,
    title,
    completed: false,
    createdAt: new Date().toISOString(),
  };
  todos.push(todo);
  return { ...todo };
}

export function update(id, patch) {
  const todo = todos.find((t) => t.id === id);
  if (!todo) return null;
  Object.assign(todo, patch);
  return { ...todo };
}

export function remove(id) {
  const index = todos.findIndex((t) => t.id === id);
  if (index === -1) return false;
  todos.splice(index, 1);
  return true;
}

// Seed a couple of items so the demo isn't empty on first load.
reset([
  { id: 1, title: "Walk through the architecture doc", completed: true, createdAt: new Date().toISOString() },
  { id: 2, title: "Run the Security + Test agents", completed: false, createdAt: new Date().toISOString() },
]);
