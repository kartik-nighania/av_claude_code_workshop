import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Proxy /api/* to the Flask backend so the browser makes same-origin requests
// (no CORS setup needed). Target is overridable for docker (backend:8000).
const target = process.env.VITE_PROXY_TARGET || "http://localhost:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      "/api": { target, changeOrigin: true },
    },
  },
});
