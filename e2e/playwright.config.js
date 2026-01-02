import dotenv from "dotenv";
dotenv.config({ path: ".env" });
import { get_test_reports_dir, artillery_record_mode } from "./client/utils";

const TEST_REPORTS_DIR = get_test_reports_dir();
const record = artillery_record_mode();

const config = {
	testDir: "client/tests",
	workers: 3,
	retries: 1,
	use: {
		actionTimeout: 5000,
		baseURL: "http://localhost:3000",
		browserName: "chromium",
		headless: false,
		trace: "on-first-retry",
	},
	reporter: [
		["github"],
		["list"],
		["html", { outputFolder: TEST_REPORTS_DIR, open: "never" }],
		["json", { outputFile: `${TEST_REPORTS_DIR}/report.json` }],
		...(record ? [["@artilleryio/playwright-reporter", { name: "Doctor Octopus UI Test Suite" }]] : []),
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
