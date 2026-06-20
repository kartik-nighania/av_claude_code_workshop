// Business logic + validation for tracked days.
// Controllers call this layer; this layer calls the store. Keep HTTP concerns
// (req/res, status codes) out of here — throw typed errors instead.

import * as store from "../store/dayStore.js";
import { HABIT_KEYS } from "../habits.js";

export class ValidationError extends Error {
  constructor(message) {
    super(message);
    this.name = "ValidationError";
    this.status = 400;
  }
}

export class NotFoundError extends Error {
  constructor(message = "Day not found") {
    super(message);
    this.name = "NotFoundError";
    this.status = 404;
  }
}

const DATE_RE = /^\d{4}-\d{2}-\d{2}$/;

// Validates that `date` is a real calendar date in YYYY-MM-DD form.
export function validateDate(date) {
  if (typeof date !== "string" || !DATE_RE.test(date)) {
    throw new ValidationError("date must be in YYYY-MM-DD format");
  }
  const parsed = new Date(`${date}T00:00:00.000Z`);
  if (Number.isNaN(parsed.getTime()) || parsed.toISOString().slice(0, 10) !== date) {
    throw new ValidationError("date is not a valid calendar date");
  }
  return date;
}

// Validates a patch of habit booleans: keys must be in the allowed set and every
// value must be a boolean. At least one habit must be present.
function validateHabitPatch(body) {
  if (typeof body !== "object" || body === null || Array.isArray(body)) {
    throw new ValidationError("request body must be an object of habit booleans");
  }
  const entries = Object.entries(body);
  if (entries.length === 0) {
    throw new ValidationError("provide at least one habit to update");
  }
  const patch = {};
  for (const [key, value] of entries) {
    if (!HABIT_KEYS.includes(key)) {
      throw new ValidationError(`unknown habit: ${key}`);
    }
    if (typeof value !== "boolean") {
      throw new ValidationError(`habit "${key}" must be a boolean`);
    }
    patch[key] = value;
  }
  return patch;
}

export function listDays() {
  return store.findAll();
}

// GET semantics: return the day, creating a default all-false day if none exists.
export function getDay(date) {
  validateDate(date);
  return store.findOrCreate(date);
}

export function updateDay(date, body) {
  validateDate(date);
  const patch = validateHabitPatch(body);
  return store.update(date, patch);
}
