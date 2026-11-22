import { defineConfig } from "@playwright/test";

const apiEnv = {
  LLM_PROVIDER: "mock",
  GITHUB_MODE: "mock",
  APP_ENV: "test",
  POC_DATABASE_URL: "sqlite:///data/e2e/poc-studio.sqlite",
  RUNS_DIR: "data/e2e/runs",
};

// The API runs on mocks against its own throwaway database (data/e2e, git-ignored), wiped on each start.
export default defineConfig({
  testDir: "./e2e",
  workers: 1,
  timeout: 60_000,
  expect: { timeout: 15_000 },
  use: { baseURL: "http://127.0.0.1:3000" },
  reporter: "list",
  webServer: [
    {
      command:
        "node -e \"require('fs').rmSync('../../data/e2e',{recursive:true,force:true})\" && uv run alembic upgrade head && uv run uvicorn poc_studio.main:app --host 127.0.0.1 --port 8000",
      cwd: "../../services/api",
      env: apiEnv,
      url: "http://127.0.0.1:8000/api/health",
      reuseExistingServer: true,
      timeout: 120_000,
    },
    {
      command: "npm run dev",
      url: "http://127.0.0.1:3000",
      reuseExistingServer: true,
      timeout: 120_000,
    },
  ],
});
