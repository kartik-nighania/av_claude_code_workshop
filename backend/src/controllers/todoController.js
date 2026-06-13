// HTTP layer: translates requests into service calls and shapes responses.
// All thrown service errors carry a `.status`; the error middleware maps them.

import * as service from "../services/todoService.js";

function parseId(raw) {
  const id = Number(raw);
  if (!Number.isInteger(id) || id < 1) {
    const err = new service.ValidationError("invalid id");
    throw err;
  }
  return id;
}

export function list(req, res) {
  res.json(service.listTodos());
}

export function getOne(req, res) {
  const id = parseId(req.params.id);
  res.json(service.getTodo(id));
}

export function create(req, res) {
  const todo = service.createTodo(req.body ?? {});
  res.status(201).json(todo);
}

export function update(req, res) {
  const id = parseId(req.params.id);
  res.json(service.updateTodo(id, req.body ?? {}));
}

export function toggle(req, res) {
  const id = parseId(req.params.id);
  res.json(service.toggleTodo(id));
}

export function remove(req, res) {
  const id = parseId(req.params.id);
  service.deleteTodo(id);
  res.status(204).end();
}
