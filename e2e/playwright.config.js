import dotenv from "dotenv";
dotenv.config({ path: ".env" });
import { get_test_reports_dir } from "./client/utils";

const TEST_REPORTS_DIR = get_test_reports_dir();

const config = {
	testDir: "client/tests",
	timeout: 30000,
	retries: 1,
	use: {
		browserName: "chromium",
		headless: false,
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
			testMatch: "ui/*.spec.js",
			use: { browserName: "chromium" },
		},
		{
			name: "ui:sanity",
			testMatch: "ui/*.spec.js",
			use: { browserName: "chromium" },
		},
		{
			name: "ui:regression",
			testMatch: "ui/*.spec.js",
			use: { browserName: "chromium" },
		},
		{
			name: "unit:smoke",
			testMatch: "unit/*.spec.js",
		},
		{
			name: "unit:sanity",
			testMatch: "unit/*.spec.js",
		},
		{
			name: "unit:regression",
			testMatch: "unit/*.spec.js",
		},
		{
			name: "db",
			testMatch: "db/*.spec.js",
		},
	],
};

export default config;
