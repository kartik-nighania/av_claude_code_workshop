// HTTP layer: translates requests into service calls and shapes responses.
// All thrown service errors carry a `.status`; the error middleware maps them.

import * as service from "../services/dayService.js";

export function list(req, res) {
  res.json(service.listDays());
}

export function getOne(req, res) {
  res.json(service.getDay(req.params.date));
}

export function update(req, res) {
  res.json(service.updateDay(req.params.date, req.body ?? {}));
}
