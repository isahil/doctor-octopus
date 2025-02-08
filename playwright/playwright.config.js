import dotenv from "dotenv"
import { get_est_date_time } from "./utils"
dotenv.config({ path: ".env" })

const { TEST_REPORTS_DIR = `./test_reports/${get_est_date_time()}` } = process.env
const config = {
  testDir: "tests",
  timeout: 30000,
  retries: 1,
  use: {
    browserName: "chromium",
    headless: true,
    trace: "on-first-retry",
  },
  reporter: [
    ["github"]
    ["list"],
    ["html", { outputFolder: TEST_REPORTS_DIR, open: "never" }],
    ["json", { outputFile: `${TEST_REPORTS_DIR}/report.json` }],
  ],
  projects: [
    {
      name: "api:smoke",
      testMatch: "test-example.spec.js",
      use: { browserName: "chromium" },
    },
    {
      name: "api:sanity",
      testMatch: "test-example.spec.js",
      use: { browserName: "chromium" },
    },
    {
      name: "api:regression",
      testMatch: "test-example.spec.js",
      use: { browserName: "chromium" },
    },
    {
      name: "ui:smoke",
      testMatch: "test-example.spec.js",
      use: { browserName: "chromium" },
    },
    {
      name: "ui:sanity",
      testMatch: "test-example.spec.js",
      use: { browserName: "chromium" },
    },
    {
      name: "ui:regression",
      testMatch: "test-example.spec.js",
      use: { browserName: "chromium" },
    },
    {
      name: "s3:smoke",
      testMatch: "s3.spec.js"
    },
  ],
}

export default config
