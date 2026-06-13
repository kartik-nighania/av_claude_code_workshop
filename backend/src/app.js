// Express app wiring. Exported separately from the server so tests can mount it
// with supertest without binding a port.

import express from "express";
import cors from "cors";
import todoRoutes from "./routes/todoRoutes.js";

export function createApp() {
  const app = express();

  app.use(cors());
  app.use(express.json());

  app.get("/health", (req, res) => res.json({ status: "ok" }));
  app.use("/api/todos", todoRoutes);

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
