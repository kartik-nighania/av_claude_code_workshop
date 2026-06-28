import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Proxy /api/* to the Flask backend (port 8010) so there's no CORS hassle in dev.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": "http://localhost:8010",
    },
  },
});
