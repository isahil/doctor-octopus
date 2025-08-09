import "dotenv/config";
import CI from "is-ci";
import os from "os";
import fs from "fs";
import { execSync } from "child_process";
import { get_est_date_time, spawn_child_process, upload_directory } from "./index.js";

const { AWS_SDET_BUCKET_NAME, ENVIRONMENT, APP } = process.env;
const test_script_name = process.argv[2];
const test_protocol = test_script_name.split(":")[0];
const app = APP ?? "loan";

const test_reports_dir = "test_reports";
const report_dir = `${get_est_date_time()}`;
const local_test_reports_dir = `./${test_reports_dir}/${report_dir}`;
process.env.TEST_REPORTS_DIR = local_test_reports_dir;
const s3_test_reports_dir = `trading-apps/${test_reports_dir}/${APP}/${ENVIRONMENT}/${test_protocol}/${report_dir}`;

const os_username = os.userInfo().username;
const git_branch = execSync("git rev-parse --abbrev-ref HEAD").toString().trim();
const json_report = `${local_test_reports_dir}/report.json`; // Need to read the report_card.json file to upload

const upload_report = async (code) => {
	const report_card = JSON.parse(fs.readFileSync(json_report, "utf-8"));

	// Add the git-branch & username to the report_card object
	report_card["stats"]["git_branch"] = git_branch;
	report_card["stats"]["username"] = os_username;
	report_card["stats"]["environment"] = ENVIRONMENT;
	report_card["stats"]["app"] = app;
	report_card["stats"]["test_suite"] = test_script_name;

	if (CI) {
		const run_id = process.env.GITHUB_RUN_ID; // e.g., 1234567890
		const repo = process.env.GITHUB_REPOSITORY; // e.g., owner/repo
		const server = process.env.GITHUB_SERVER_URL || "https://github.com";
		const run_url = run_id && repo ? `${server}/${repo}/actions/runs/${run_id}` : undefined;
		const sdet = process.env.GITHUB_ACTOR || os_username; // Use GITHUB_ACTOR or fallback to os_username

		report_card["ci"] = { run_id, run_url, sdet };
	}

	// Write the updated reportCard object back to the report.json file
	fs.writeFileSync(json_report, JSON.stringify(report_card, null, 2));
	if (CI) {
		console.log(`Uploading test reports to S3 bucket: ${AWS_SDET_BUCKET_NAME}`);
		await upload_directory(AWS_SDET_BUCKET_NAME, local_test_reports_dir, s3_test_reports_dir);
	}
	process.exit(code ?? 1);
};

spawn_child_process(`npx playwright test --project=${test_script_name}`, upload_report);
