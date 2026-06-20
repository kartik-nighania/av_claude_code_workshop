// In-memory data store for tracked days.
// Swap this module for a real DB (Postgres/SQLite) in the lab — the service
// layer only depends on the functions exported here, not on the storage.
//
// A day is keyed by its ISO date (YYYY-MM-DD) and holds one boolean per habit.

import { HABIT_KEYS } from "../habits.js";

let days = new Map();

function defaultHabits() {
  return Object.fromEntries(HABIT_KEYS.map((key) => [key, false]));
}

function shape(date, habits) {
  return { date, habits: { ...habits } };
}

export function reset(seed = []) {
  days = new Map();
  for (const { date, habits } of seed) {
    days.set(date, { ...defaultHabits(), ...habits });
  }
}

export function findAll() {
  return [...days.entries()]
    .map(([date, habits]) => shape(date, habits))
    .sort((a, b) => a.date.localeCompare(b.date));
}

export function findByDate(date) {
  const habits = days.get(date);
  return habits ? shape(date, habits) : null;
}

// Returns the existing day, or creates and returns a fresh all-false day.
export function findOrCreate(date) {
  if (!days.has(date)) days.set(date, defaultHabits());
  return shape(date, days.get(date));
}

export function update(date, patch) {
  if (!days.has(date)) days.set(date, defaultHabits());
  const habits = days.get(date);
  Object.assign(habits, patch);
  return shape(date, habits);
}

// Seed a couple of days so the demo isn't empty on first load.
reset([
  { date: "2026-06-19", habits: { water: true, steps: true, sleep: false, meditate: true } },
  { date: "2026-06-20", habits: { water: true, steps: false, sleep: false, meditate: false } },
]);
