// Unit tests for the thin API client. Runs in Vitest's default (node)
// environment — no DOM needed; global `fetch` is stubbed per-test.
import { describe, it, expect, vi, afterEach } from "vitest";
import { api } from "./api.js";

afterEach(() => {
  vi.unstubAllGlobals();
});

function stubFetch(impl) {
  const mock = vi.fn(impl);
  vi.stubGlobal("fetch", mock);
  return mock;
}

describe("api client", () => {
  it("habits() GETs /api/habits and returns parsed JSON", async () => {
    const fetchMock = stubFetch(async () => ({
      ok: true,
      status: 200,
      json: async () => [{ key: "water", label: "Water" }],
    }));

    const result = await api.habits();

    expect(fetchMock).toHaveBeenCalledWith("/api/habits");
    expect(result).toEqual([{ key: "water", label: "Water" }]);
  });

  it("getDay() returns null on a 204 No Content", async () => {
    stubFetch(async () => ({
      ok: true,
      status: 204,
      json: async () => {
        throw new Error("body should not be read on 204");
      },
    }));

    await expect(api.getDay("2026-06-20")).resolves.toBeNull();
  });

  it("surfaces the server error message when the response is not ok", async () => {
    stubFetch(async () => ({
      ok: false,
      status: 400,
      json: async () => ({ error: "date must be in YYYY-MM-DD format" }),
    }));

    await expect(api.getDay("bad")).rejects.toThrow("date must be in YYYY-MM-DD format");
  });

  it("updateDay() sends a PATCH with a JSON body", async () => {
    const fetchMock = stubFetch(async () => ({
      ok: true,
      status: 200,
      json: async () => ({ date: "2026-06-20", habits: { water: true } }),
    }));

    const result = await api.updateDay("2026-06-20", { water: true });

    expect(fetchMock).toHaveBeenCalledWith("/api/days/2026-06-20", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ water: true }),
    });
    expect(result).toEqual({ date: "2026-06-20", habits: { water: true } });
  });
});
