// Runs a named group of checks (lint, typecheck, test) in order; stops at the first failure.
// Usage: node scripts/run-all.mjs <lint|typecheck|test>
import { spawnSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const api = join(root, "services", "api");

const groups = {
  lint: [
    [api, "uv", ["run", "ruff", "check", "."]],
    [root, "npm", ["--workspace", "apps/web", "run", "lint"]],
  ],
  typecheck: [
    [api, "uv", ["run", "pyright", "poc_studio"]],
    // typegen emits the route types (LayoutProps etc.) that a clean checkout lacks
    [root, "npm", ["--workspace", "apps/web", "exec", "--", "next", "typegen"]],
    [root, "npm", ["--workspace", "apps/web", "exec", "--", "tsc", "--noEmit"]],
  ],
  test: [
    [api, "uv", ["run", "pytest", "-q", "-m", "not slow and not live"]],
    [root, "npm", ["--workspace", "apps/web", "test"]],
  ],
};

const steps = groups[process.argv[2] ?? ""];
if (!steps) {
  console.error(`Usage: run-all.mjs <${Object.keys(groups).join("|")}>`);
  process.exit(2);
}

for (const [cwd, cmd, args] of steps) {
  console.log(`\n> ${cmd} ${args.join(" ")}  (${cwd === root ? "." : "services/api"})`);
  // Windows needs a shell to resolve npm.cmd/uv; quote args with spaces because the shell re-splits them.
  const win = process.platform === "win32";
  const argv = win ? args.map((a) => (/\s/.test(a) ? `"${a}"` : a)) : args;
  const res = spawnSync(cmd, argv, { cwd, stdio: "inherit", shell: win });
  if (res.status !== 0) process.exit(res.status ?? 1);
}
