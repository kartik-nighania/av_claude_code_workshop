// ESLint flat config (v9) for the frontend.
// Recommended JS + React rules with browser globals. React 18 uses the
// automatic JSX runtime, so `react-in-jsx-scope` is off; this codebase doesn't
// use prop-types, so that rule is off too.
import js from "@eslint/js";
import globals from "globals";
import react from "eslint-plugin-react";

export default [
  // Never lint build output or coverage reports.
  { ignores: ["dist/**", "coverage/**"] },
  js.configs.recommended,
  {
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "module",
      parserOptions: { ecmaFeatures: { jsx: true } },
      globals: { ...globals.browser },
    },
    plugins: { react },
    settings: { react: { version: "detect" } },
    rules: {
      ...react.configs.recommended.rules,
      "react/react-in-jsx-scope": "off",
      "react/prop-types": "off",
    },
  },
  {
    files: ["**/*.test.{js,jsx}"],
    languageOptions: {
      globals: { ...globals.node },
    },
  },
];
