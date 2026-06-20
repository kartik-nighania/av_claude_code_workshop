// Express app wiring. Exported separately from the server so tests can mount it
// with supertest without binding a port.

import express from "express";
import cors from "cors";
import dayRoutes from "./routes/dayRoutes.js";
import { HABITS } from "./habits.js";

export function createApp() {
  const app = express();

  app.use(cors());
  app.use(express.json());

  app.get("/health", (req, res) => res.json({ status: "ok" }));
  // Exposes the fixed habit definitions so the UI can render labels.
  app.get("/api/habits", (req, res) => res.json(HABITS));
  app.use("/api/days", dayRoutes);

  // 404 for anything unmatched.
  app.use((req, res) => {
    res.status(404).json({ error: "Not found" });
  });

  // Central error handler — maps typed service errors to HTTP responses.
  // eslint-disable-next-line no-unused-vars
  app.use((err, req, res, next) => {
    const status = err.status ?? 500;
    if (status === 500) console.error(err);
    res.status(status).json({ error: err.message ?? "Internal server error" });
  });

  return app;
}
