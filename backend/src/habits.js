// The fixed set of daily health habits the app tracks. Single source of truth
// shared by the store (defaults) and the service (validation).

export const HABITS = [
  { key: "water", label: "Drank enough water" },
  { key: "steps", label: "Hit 10k steps" },
  { key: "sleep", label: "Slept well (8h)" },
  { key: "meditate", label: "Meditated" },
];

export const HABIT_KEYS = HABITS.map((h) => h.key);
