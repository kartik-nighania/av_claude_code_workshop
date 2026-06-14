#!/usr/bin/env node
// driver.mjs — boot + drive the Multi-Agent TODO Lab end-to-end.
//
// Zero dependencies: built-in fetch + child_process + a headless Chrome you
// already have. Run from the repo root:
//
//   node .claude/skills/run-todo-lab/driver.mjs            # full run (API smoke + screenshot)
//   node .claude/skills/run-todo-lab/driver.mjs --api-only # backend CRUD smoke only, no browser
//   node .claude/skills/run-todo-lab/driver.mjs --screenshot-only  # boot servers + screenshot only
//
// Chrome binary resolves via $CHROME_BIN, then the macOS default, then
// google-chrome/chromium on PATH (so the same script works on Linux CI).

import { spawn, spawnSync } from "node:child_process";
import { existsSync, mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

// Repo root is two levels up from .claude/skills/run-todo-lab/.
const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "../../..");
const BACKEND = "http://localhost:3001";
const FRONTEND = "http://localhost:5173";
const SHOT = resolve(ROOT, "docs/screenshots/todo-app.png");

const args = new Set(process.argv.slice(2));
const apiOnly = args.has("--api-only");
const screenshotOnly = args.has("--screenshot-only");

const children = [];
let failures = 0;

function log(msg) { process.stdout.write(`▸ ${msg}\n`); }
function ok(msg)  { process.stdout.write(`  \x1b[32m✓\x1b[0m ${msg}\n`); }
function bad(msg) { failures++; process.stdout.write(`  \x1b[31m✗ ${msg}\x1b[0m\n`); }

function assert(cond, msg) { cond ? ok(msg) : bad(msg); }

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function waitFor(url, label, tries = 50) {
  for (let i = 0; i < tries; i++) {
    try {
      const res = await fetch(url);
      if (res.ok) return res;
    } catch { /* not up yet */ }
    await sleep(200);
  }
  throw new Error(`${label} did not come up at ${url}`);
}

function spawnServer(cmd, cmdArgs, label) {
  const child = spawn(cmd, cmdArgs, { cwd: ROOT, stdio: ["ignore", "pipe", "pipe"] });
  children.push(child);
  child.stderr.on("data", (d) => {
    const s = d.toString();
    if (/error/i.test(s)) process.stderr.write(`[${label}] ${s}`);
  });
  return child;
}

function findChrome() {
  if (process.env.CHROME_BIN && existsSync(process.env.CHROME_BIN)) return process.env.CHROME_BIN;
  const mac = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
  if (existsSync(mac)) return mac;
  for (const bin of ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser"]) {
    const which = spawnSync("command", ["-v", bin], { shell: true, encoding: "utf8" });
    if (which.status === 0 && which.stdout.trim()) return which.stdout.trim();
  }
  return null;
}

// ── Step 1+2: backend boot + CRUD/validation smoke ────────────────────────
async function apiSmoke() {
  log("Booting backend (node backend/src/server.js)…");
  spawnServer("node", ["backend/src/server.js"], "backend");
  await waitFor(`${BACKEND}/health`, "backend");
  ok("backend healthy at " + BACKEND);

  log("API smoke: full CRUD + validation against /api/todos");

  const seed = await (await fetch(`${BACKEND}/api/todos`)).json();
  assert(Array.isArray(seed) && seed.length >= 2, `GET list returns seed todos (${seed.length})`);

  const created = await fetch(`${BACKEND}/api/todos`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title: "driver smoke item" }),
  });
  const todo = await created.json();
  assert(created.status === 201 && todo.id && todo.completed === false,
    `POST creates todo (201, id=${todo.id})`);

  const got = await fetch(`${BACKEND}/api/todos/${todo.id}`);
  assert(got.status === 200 && (await got.json()).title === "driver smoke item",
    "GET /:id returns the created todo");

  const toggled = await fetch(`${BACKEND}/api/todos/${todo.id}/toggle`, { method: "PATCH" });
  assert(toggled.status === 200 && (await toggled.json()).completed === true,
    "PATCH /:id/toggle flips completed");

  const updated = await fetch(`${BACKEND}/api/todos/${todo.id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title: "renamed by driver" }),
  });
  assert(updated.status === 200 && (await updated.json()).title === "renamed by driver",
    "PUT /:id updates title");

  const del = await fetch(`${BACKEND}/api/todos/${todo.id}`, { method: "DELETE" });
  assert(del.status === 204, "DELETE /:id returns 204");

  const gone = await fetch(`${BACKEND}/api/todos/${todo.id}`);
  assert(gone.status === 404, "GET deleted todo returns 404");

  const empty = await fetch(`${BACKEND}/api/todos`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title: "   " }),
  });
  const emptyBody = await empty.json();
  assert(empty.status === 400 && /title is required/.test(emptyBody.error),
    "POST blank title rejected (400 title is required)");

  const badId = await fetch(`${BACKEND}/api/todos/abc`);
  assert(badId.status === 400, "GET non-numeric id rejected (400)");
}

// ── Step 3+4: frontend boot + headless-Chrome screenshot of the live UI ────
async function uiScreenshot() {
  if (apiOnly) return;

  // Backend must be up for the UI to render data (proxied via Vite).
  if (screenshotOnly) {
    log("Booting backend (node backend/src/server.js)…");
    spawnServer("node", ["backend/src/server.js"], "backend");
    await waitFor(`${BACKEND}/health`, "backend");
    ok("backend healthy");
  }

  log("Booting frontend (npm run dev:frontend → Vite :5173)…");
  spawnServer("npm", ["run", "dev:frontend"], "frontend");
  await waitFor(FRONTEND, "frontend");
  ok("frontend serving at " + FRONTEND);

  // Add a distinctive todo via the API so the screenshot proves the round-trip.
  await fetch(`${BACKEND}/api/todos`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title: "★ added by driver — end-to-end proof" }),
  });
  ok("seeded a distinctive todo via the API");

  const chrome = findChrome();
  if (!chrome) { bad("no Chrome/Chromium found (set $CHROME_BIN)"); return; }

  mkdirSync(dirname(SHOT), { recursive: true });
  log(`Screenshotting ${FRONTEND} with headless Chrome…`);
  // --virtual-time-budget gives React time to mount + the /api/todos fetch to
  // resolve before capture. headless=new usually waits for load on its own, but
  // this makes a populated UI deterministic on a cold/slow first paint.
  const shot = spawnSync(chrome, [
    "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-sandbox",
    "--virtual-time-budget=6000", "--window-size=900,1000",
    `--screenshot=${SHOT}`, FRONTEND,
  ], { encoding: "utf8" });
  assert(shot.status === 0 && existsSync(SHOT), `screenshot written → ${SHOT}`);
}

async function main() {
  try {
    if (!screenshotOnly) await apiSmoke();
    await uiScreenshot();
  } catch (e) {
    bad(e.message);
  } finally {
    for (const c of children) { try { c.kill("SIGTERM"); } catch { /* ignore */ } }
    await sleep(300);
  }
  process.stdout.write(failures === 0
    ? "\n\x1b[32mAll checks passed.\x1b[0m\n"
    : `\n\x1b[31m${failures} check(s) failed.\x1b[0m\n`);
  process.exit(failures === 0 ? 0 : 1);
}

main();
