import dotenv from "dotenv"
dotenv.config({ path: ".env" })

const { TEST_REPORTS_DIR } = process.env // TODO: copy logic from run.js to create the TEST_REPORTS_DIR
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
