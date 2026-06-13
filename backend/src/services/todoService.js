// Business logic + validation for todos.
// Controllers call this layer; this layer calls the store. Keep HTTP concerns
// (req/res, status codes) out of here — throw typed errors instead.

import * as store from "../store/todoStore.js";

const MAX_TITLE_LENGTH = 280;

export class ValidationError extends Error {
  constructor(message) {
    super(message);
    this.name = "ValidationError";
    this.status = 400;
  }
}

export class NotFoundError extends Error {
  constructor(message = "Todo not found") {
    super(message);
    this.name = "NotFoundError";
    this.status = 404;
  }
}

function validateTitle(title) {
  if (typeof title !== "string" || title.trim().length === 0) {
    throw new ValidationError("title is required");
  }
  if (title.length > MAX_TITLE_LENGTH) {
    throw new ValidationError(`title must be ${MAX_TITLE_LENGTH} characters or fewer`);
  }
  return title.trim();
}

export function listTodos() {
  return store.findAll();
}

export function getTodo(id) {
  const todo = store.findById(id);
  if (!todo) throw new NotFoundError();
  return todo;
}

export function createTodo({ title }) {
  const clean = validateTitle(title);
  return store.insert({ title: clean });
}

export function updateTodo(id, { title, completed }) {
  const existing = store.findById(id);
  if (!existing) throw new NotFoundError();

  const patch = {};
  if (title !== undefined) patch.title = validateTitle(title);
  if (completed !== undefined) {
    if (typeof completed !== "boolean") {
      throw new ValidationError("completed must be a boolean");
    }
    patch.completed = completed;
  }
  return store.update(id, patch);
}

export function toggleTodo(id) {
  const existing = store.findById(id);
  if (!existing) throw new NotFoundError();
  return store.update(id, { completed: !existing.completed });
}

export function deleteTodo(id) {
  const ok = store.remove(id);
  if (!ok) throw new NotFoundError();
  return true;
}
