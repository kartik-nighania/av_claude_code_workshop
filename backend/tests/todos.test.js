// Starter integration tests for the TODO API.
// This is the seed the Test agent expands in the hands-on lab — it already
// covers the happy path + a few error scenarios so `npm test` is green on day 0.

import request from "supertest";
import { createApp } from "../src/app.js";
import { reset } from "../src/store/todoStore.js";

const app = createApp();

beforeEach(() => {
  reset([{ id: 1, title: "Seed todo", completed: false, createdAt: new Date().toISOString() }]);
});

describe("GET /api/todos", () => {
  it("returns the list of todos", async () => {
    const res = await request(app).get("/api/todos");
    expect(res.status).toBe(200);
    expect(res.body).toHaveLength(1);
    expect(res.body[0].title).toBe("Seed todo");
  });
});

describe("POST /api/todos", () => {
  it("creates a todo and returns 201", async () => {
    const res = await request(app).post("/api/todos").send({ title: "New task" });
    expect(res.status).toBe(201);
    expect(res.body).toMatchObject({ title: "New task", completed: false });
    expect(res.body.id).toBeDefined();
  });

  it("rejects an empty title with 400", async () => {
    const res = await request(app).post("/api/todos").send({ title: "   " });
    expect(res.status).toBe(400);
    expect(res.body.error).toMatch(/title is required/);
  });

  it("rejects an over-long title with 400", async () => {
    const res = await request(app).post("/api/todos").send({ title: "x".repeat(281) });
    expect(res.status).toBe(400);
  });
});

describe("PATCH /api/todos/:id/toggle", () => {
  it("flips the completed flag", async () => {
    const res = await request(app).patch("/api/todos/1/toggle");
    expect(res.status).toBe(200);
    expect(res.body.completed).toBe(true);
  });

  it("returns 404 for an unknown id", async () => {
    const res = await request(app).patch("/api/todos/999/toggle");
    expect(res.status).toBe(404);
  });
});

describe("DELETE /api/todos/:id", () => {
  it("removes a todo and returns 204", async () => {
    const res = await request(app).delete("/api/todos/1");
    expect(res.status).toBe(204);
    const list = await request(app).get("/api/todos");
    expect(list.body).toHaveLength(0);
  });
});
