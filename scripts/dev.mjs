// Starts the API and the web app together; Ctrl+C stops both.
import { spawn, spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const isWin = process.platform === "win32";
const children = [];

function start(name, cmd, args, cwd) {
  const child = spawn(cmd, args, { cwd, stdio: "inherit", shell: isWin });
  child.on("exit", (code) => {
    console.log(`[dev] ${name} exited (${code ?? "signal"})`);
    shutdown(code ?? 0);
  });
  children.push(child);
}

function kill(child) {
  if (child.exitCode !== null || !child.pid) return;
  if (isWin) spawnSync("taskkill", ["/pid", String(child.pid), "/T", "/F"], { stdio: "ignore" });
  else child.kill("SIGTERM");
}

let stopping = false;
function shutdown(code = 0) {
  if (stopping) return;
  stopping = true;
  children.forEach(kill);
  process.exit(code);
}

process.on("SIGINT", () => shutdown(0));
process.on("SIGTERM", () => shutdown(0));

start(
  "api",
  "uv",
  ["run", "uvicorn", "poc_studio.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"],
  join(root, "services", "api"),
);

if (existsSync(join(root, "apps", "web", "package.json"))) {
  start("web", "npm", ["--workspace", "apps/web", "run", "dev"], root);
} else {
  console.log("[dev] apps/web does not exist yet; starting the API only.");
}
