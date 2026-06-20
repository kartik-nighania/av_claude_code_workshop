// ESLint flat config (v9) for the backend.
// Recommended JS rules + Node/ESM globals; Jest globals for the test files.
import js from "@eslint/js";
import globals from "globals";

export default [
  js.configs.recommended,
  {
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "module",
      globals: { ...globals.node },
    },
  },
  {
    files: ["tests/**/*.js", "**/*.test.js"],
    languageOptions: {
      globals: { ...globals.jest },
    },
  },
];
