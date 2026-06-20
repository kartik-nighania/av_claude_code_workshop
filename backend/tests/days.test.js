// Starter integration tests for the Health Tracker API.
// This is the seed the Test agent expands in the hands-on lab — it already
// covers the happy path + a few error scenarios so `npm test` is green on day 0.

import request from "supertest";
import { createApp } from "../src/app.js";
import { reset } from "../src/store/dayStore.js";

const app = createApp();

beforeEach(() => {
  reset([
    { date: "2026-06-20", habits: { water: true, steps: false, sleep: false, meditate: false } },
  ]);
});

describe("GET /api/habits", () => {
  it("returns the fixed habit definitions", async () => {
    const res = await request(app).get("/api/habits");
    expect(res.status).toBe(200);
    expect(res.body.map((h) => h.key)).toEqual(["water", "steps", "sleep", "meditate"]);
  });
});

describe("GET /api/days/:date", () => {
  it("returns an existing day's habit state", async () => {
    const res = await request(app).get("/api/days/2026-06-20");
    expect(res.status).toBe(200);
    expect(res.body).toEqual({
      date: "2026-06-20",
      habits: { water: true, steps: false, sleep: false, meditate: false },
    });
  });

  it("creates a default all-false day when none exists", async () => {
    const res = await request(app).get("/api/days/2026-01-01");
    expect(res.status).toBe(200);
    expect(res.body.habits).toEqual({
      water: false,
      steps: false,
      sleep: false,
      meditate: false,
    });
  });

  it("rejects a malformed date with 400", async () => {
    const res = await request(app).get("/api/days/06-20-2026");
    expect(res.status).toBe(400);
    expect(res.body.error).toMatch(/YYYY-MM-DD/);
  });

  it("rejects an impossible calendar date with 400", async () => {
    const res = await request(app).get("/api/days/2026-13-40");
    expect(res.status).toBe(400);
  });
});

describe("PATCH /api/days/:date", () => {
  it("toggles a single habit and persists it", async () => {
    const res = await request(app).patch("/api/days/2026-06-20").send({ steps: true });
    expect(res.status).toBe(200);
    expect(res.body.habits.steps).toBe(true);

    const after = await request(app).get("/api/days/2026-06-20");
    expect(after.body.habits.steps).toBe(true);
  });

  it("updates multiple habits at once", async () => {
    const res = await request(app)
      .patch("/api/days/2026-06-20")
      .send({ sleep: true, meditate: true });
    expect(res.status).toBe(200);
    expect(res.body.habits).toMatchObject({ sleep: true, meditate: true });
  });

  it("creates the day if it does not exist yet", async () => {
    const res = await request(app).patch("/api/days/2026-07-04").send({ water: true });
    expect(res.status).toBe(200);
    expect(res.body.habits).toEqual({
      water: true,
      steps: false,
      sleep: false,
      meditate: false,
    });
  });

  it("rejects an unknown habit key with 400", async () => {
    const res = await request(app).patch("/api/days/2026-06-20").send({ running: true });
    expect(res.status).toBe(400);
    expect(res.body.error).toMatch(/unknown habit/);
  });

  it("rejects a non-boolean habit value with 400", async () => {
    const res = await request(app).patch("/api/days/2026-06-20").send({ water: "yes" });
    expect(res.status).toBe(400);
    expect(res.body.error).toMatch(/must be a boolean/);
  });

  it("rejects an empty body with 400", async () => {
    const res = await request(app).patch("/api/days/2026-06-20").send({});
    expect(res.status).toBe(400);
  });

  it("rejects a malformed date with 400", async () => {
    const res = await request(app).patch("/api/days/not-a-date").send({ water: true });
    expect(res.status).toBe(400);
  });
});

describe("GET /api/days", () => {
  it("returns the tracked-day history sorted by date", async () => {
    reset([
      { date: "2026-06-20", habits: { water: true } },
      { date: "2026-06-18", habits: { steps: true } },
    ]);
    const res = await request(app).get("/api/days");
    expect(res.status).toBe(200);
    expect(res.body.map((d) => d.date)).toEqual(["2026-06-18", "2026-06-20"]);
  });
});
