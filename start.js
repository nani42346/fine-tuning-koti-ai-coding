/**
 * Koti AI Coding - one command launcher.
 *
 *   npm start            -> starts the Python API (port 8000) AND the React web page (port 3000)
 *   npm run api          -> API only
 *   npm run web          -> web page only
 *
 * No need to activate the venv manually: the venv's Python is used directly.
 * Press Ctrl+C once to stop everything.
 */
const { spawn, spawnSync } = require("child_process");
const fs = require("fs");
const http = require("http");
const net = require("net");
const path = require("path");

const ROOT = __dirname;
const WEB_DIR = path.join(ROOT, "frontend", "coding-ai-ui");
const IS_WIN = process.platform === "win32";
const VENV_PY = IS_WIN
  ? path.join(ROOT, "venv", "Scripts", "python.exe")
  : path.join(ROOT, "venv", "bin", "python");

const args = process.argv.slice(2);
const runApi = !args.includes("--web-only");
const runWeb = !args.includes("--api-only");

const C = { api: "\x1b[35m", web: "\x1b[36m", ok: "\x1b[32m", warn: "\x1b[33m", err: "\x1b[31m", dim: "\x1b[2m", reset: "\x1b[0m" };
const log = (color, tag, msg) => console.log(`${color}[${tag}]${C.reset} ${msg}`);

const children = [];

function pipe(child, tag, color, filter) {
  const handle = (buf) => {
    buf
      .toString()
      .split(/\r?\n/)
      .forEach((line) => {
        if (!line.trim()) return;
        if (filter && !filter(line)) return;
        console.log(`${color}[${tag}]${C.reset} ${line}`);
      });
  };
  child.stdout && child.stdout.on("data", handle);
  child.stderr && child.stderr.on("data", handle);
}

// true if something is already listening on the port (any interface)
function portInUse(port) {
  const tryConnect = (host) =>
    new Promise((resolve) => {
      const sock = net.connect({ port, host });
      sock.setTimeout(800);
      sock.once("connect", () => {
        sock.destroy();
        resolve(true);
      });
      sock.once("timeout", () => {
        sock.destroy();
        resolve(false);
      });
      sock.once("error", () => resolve(false));
    });
  return Promise.all([tryConnect("127.0.0.1"), tryConnect("::1")]).then((r) => r.some(Boolean));
}

function apiHealthy() {
  return new Promise((resolve) => {
    const req = http.get("http://127.0.0.1:8000/", { timeout: 2000 }, (res) => {
      res.resume();
      resolve(res.statusCode === 200);
    });
    req.on("error", () => resolve(false));
    req.on("timeout", () => {
      req.destroy();
      resolve(false);
    });
  });
}

async function startApi() {
  if (!fs.existsSync(VENV_PY)) {
    log(C.err, "API", `Python venv not found at ${VENV_PY}`);
    log(C.err, "API", "Create it with:  python -m venv venv  and install the requirements.");
    return false;
  }
  if (await portInUse(8000)) {
    if (await apiHealthy()) {
      log(C.ok, "API", "Already running on http://127.0.0.1:8000 - reusing it.");
      return true;
    }
    log(C.err, "API", "Port 8000 is busy with another program. Close it and run npm start again.");
    return false;
  }

  log(C.api, "API", "Starting Koti AI Coding API on http://127.0.0.1:8000 (model loads in ~15s)...");
  const api = spawn(VENV_PY, ["-m", "uvicorn", "api:app", "--host", "127.0.0.1", "--port", "8000"], {
    cwd: ROOT,
    env: { ...process.env, PYTHONUNBUFFERED: "1", PYTHONIOENCODING: "utf-8" },
  });
  children.push(api);
  // hide the noisy weight-loading progress bar
  pipe(api, "API", C.api, (line) => !line.includes("Loading weights"));
  api.on("exit", (code) => {
    if (!shuttingDown) log(C.err, "API", `API stopped (exit code ${code}). See the messages above.`);
  });

  // wait until the model is ready
  for (let i = 0; i < 180; i++) {
    await new Promise((r) => setTimeout(r, 1000));
    if (api.exitCode !== null) return false;
    if (await apiHealthy()) {
      log(C.ok, "API", "Model ready - API online.");
      return true;
    }
  }
  log(C.warn, "API", "API is taking long to start, continuing anyway...");
  return true;
}

async function startWeb() {
  if (await portInUse(3000)) {
    log(C.ok, "WEB", "Web dashboard is already running - open http://localhost:3000");
    log(C.dim, "WEB", "(It picks up code changes automatically. To restart it, close the old terminal first.)");
    return;
  }
  if (!fs.existsSync(path.join(WEB_DIR, "node_modules"))) {
    log(C.web, "WEB", "Installing frontend packages (first run only)...");
    const r = spawnSync("npm install", { cwd: WEB_DIR, shell: true, stdio: "inherit" });
    if (r.status !== 0) {
      log(C.err, "WEB", "npm install failed.");
      return;
    }
  }
  log(C.web, "WEB", "Starting web dashboard on http://localhost:3000 ...");
  const web = spawn("npm start", {
    cwd: WEB_DIR,
    shell: true,
    env: { ...process.env, FORCE_COLOR: "1" },
  });
  children.push(web);
  pipe(web, "WEB", C.web);
  web.on("exit", (code) => {
    if (!shuttingDown) log(C.err, "WEB", `Web server stopped (exit code ${code}).`);
  });
}

let shuttingDown = false;
function shutdown() {
  if (shuttingDown) return;
  shuttingDown = true;
  console.log(`\n${C.dim}Stopping Koti AI Coding...${C.reset}`);
  for (const c of children) {
    if (c.exitCode !== null) continue;
    if (IS_WIN) spawnSync("taskkill", ["/pid", String(c.pid), "/T", "/F"], { stdio: "ignore" });
    else c.kill("SIGTERM");
  }
  process.exit(0);
}
process.on("SIGINT", shutdown);
process.on("SIGTERM", shutdown);

(async () => {
  console.log(`\n${C.api}  ✦ Koti AI Coding${C.reset}  ${C.dim}API + Dashboard launcher${C.reset}\n`);
  if (runApi) {
    const ok = await startApi();
    if (!ok && !runWeb) process.exit(1);
  }
  if (runWeb) await startWeb();
  console.log(`${C.dim}Press Ctrl+C to stop everything.${C.reset}`);
})();
