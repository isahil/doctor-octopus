import "dotenv/config";
import { PlaywrightTestConfig } from "playwright/test";
 
const { TEST_REPORTS_DIR } = process.env;

const config: PlaywrightTestConfig = {
  testDir: "tests",
  // globalSetup: require.resolve("./global.setup.js"),
  timeout: 30000,
  retries: 1,
  use: {
    browserName: 'chromium',
    headless: true,
    trace: "on-first-retry"
  },
  reporter: [
    ['list'],
    ['html', { outputFolder: TEST_REPORTS_DIR, open: "never" } ],
    ['json', { outputFile: `${TEST_REPORTS_DIR}/report.json` }],
  ],
  projects: [
    {
      name: 'api:smoke',
      testMatch: 'test-example.spec.ts',
      use: { browserName: 'chromium'}
    },
    {
      name: 'api:sanity',
      testMatch: 'test-example.spec.ts',
      use: { browserName: 'chromium' }
    },
    {
      name: 'api:regression',
      testMatch: 'test-example.spec.ts',
      use: { browserName: 'chromium' }
    },
    {
      name: 'ui:smoke',
      testMatch: 'test-example.spec.ts',
      use: { browserName: 'chromium' }
    },
    {
      name: 'ui:sanity',
      testMatch: 'test-example.spec.ts',
      use: { browserName: 'chromium' }
    },
    {
      name: 'ui:regression',
      testMatch: 'test-example.spec.ts',
      use: { browserName: 'chromium' }
    }
  ]
};

export default config;