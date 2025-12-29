import dotenv from "dotenv";
dotenv.config({ path: ".env" });
import { get_est_date_time } from "./client/utils";

const { TEST_REPORTS_DIR = `./test_reports/${get_est_date_time()}` } =
  process.env;
const config = {
  testDir: "client/tests",
  timeout: 30000,
  retries: 1,
  use: {
    browserName: "chromium",
    headless: true,
    trace: "on-first-retry",
  },
  reporter: [
    ["github"],
    ["list"],
    ["html", { outputFolder: TEST_REPORTS_DIR, open: "never" }],
    ["json", { outputFile: `${TEST_REPORTS_DIR}/report.json` }],
  ],
  projects: [
    {
      name: "ui:smoke",
      testMatch: "unit/test-example.spec.js",
      use: { browserName: "chromium" },
    },
    {
      name: "ui:sanity",
      testMatch: "unit/test-example.spec.js",
      use: { browserName: "chromium" },
    },
    {
      name: "ui:regression",
      testMatch: "unit/test-example.spec.js",
      use: { browserName: "chromium" },
    },
    {
      name: "unit",
      testMatch: "unit/*.spec.js",
    },
    {
      name: "db",
      testMatch: "db/*.spec.js",
    },
  ],
};

export default config;
