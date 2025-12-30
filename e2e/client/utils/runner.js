import "dotenv/config";
import {
	gh_actions_debug_mode,
	get_test_reports_dir,
	spawn_child_process,
	upload_report,
} from "./index.js";

const test_suite = process.argv[2] ?? "";
const runner = process.argv[3] ?? "playwright";
const gh_actions_debug = gh_actions_debug_mode();
const full_test_reports_dir = get_test_reports_dir();

const upload_report_directory = async (code) => {
	await upload_report(code, { test_suite, full_test_reports_dir });
};

const log_level = gh_actions_debug ? "LOG_LEVEL=trace" : "LOG_LEVEL=info";
const runner_command =
	runner.toLowerCase() === "pytest"
		? `poetry run pytest ${test_suite} --html=${full_test_reports_dir}/index.html --json-report-file=${full_test_reports_dir}/report.json`
		: `npx playwright test --project=${test_suite}`;
const command = log_level ? `${log_level} ${runner_command}` : `${runner_command}`;

spawn_child_process(command, upload_report_directory);
