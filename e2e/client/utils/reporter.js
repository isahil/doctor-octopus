import is_ci from "is-ci";
import os from "os";
import fs from "fs";
import { execSync } from "child_process";
import { upload_directory } from "./index.js";
import {
	get_environment,
	get_app_name,
	get_product,
	get_aws_sdet_bucket_name,
	get_github_run_id,
	get_github_repository,
	get_github_server_url,
	get_github_actor,
	artillery_record_mode
} from "./env_loader.js";

const delimeter = test_suite => {
	return test_suite.includes(":") ? ":" : "_";
}

export const upload_report = async (code, { test_suite, json_report, full_test_reports_dir, runner }) => {
	const test_reports_dir = "test_reports";
	const environment = get_environment();
	const product = get_product();
	const app_name = get_app_name();
	const aws_sdet_bucket_name = get_aws_sdet_bucket_name();
	const record = artillery_record_mode();
	// Changing the report pattern can break report cards feature
	const test_protocol = test_suite.split(delimeter(test_suite))[0];
	const report_dir = full_test_reports_dir.split("/").pop();
	const s3_test_reports_dir = `trading-apps/${test_reports_dir}/${product}/${environment}/${test_protocol}/${report_dir}`;
	// json_report = json_report ?? `${full_test_reports_dir}/report.json`;
	// const report_card = JSON.parse(fs.readFileSync(json_report, "utf-8"));

	// // Add meta data below
	// const os_username = os.userInfo().username;
	// const git_branch = execSync("git rev-parse --abbrev-ref HEAD").toString().trim();
	// report_card["stats"] ??= {};
	// report_card["stats"]["app"] = product;
	// report_card["stats"]["app_name"] = app_name;
	// report_card["stats"]["environment"] = environment;
	// report_card["stats"]["git_branch"] = git_branch;
	// report_card["stats"]["protocol"] = test_protocol;
	// report_card["stats"]["product"] = product;
	// report_card["stats"]["runner"] = runner;
	// report_card["stats"]["test_reports_dir"] = test_reports_dir;
	// report_card["stats"]["test_suite"] = test_suite;
	// report_card["stats"]["username"] = os_username;

	// if (is_ci) {
	// 	const run_id = get_github_run_id(); // e.g., 1234567890
	// 	const repo = get_github_repository(); // e.g., owner/repo
	// 	const server = get_github_server_url() || "https://github.com";
	// 	const run_url = run_id && repo ? `${server}/${repo}/actions/runs/${run_id}` : "na";
	// 	const sdet = get_github_actor() || os_username;
	// 	report_card["ci"] = { run_id, run_url, sdet };
	// }

	// // Write the updated report_card object back to the report.json file
	// fs.writeFileSync(json_report, JSON.stringify(report_card, null, 2));

	if (!is_ci && !record) return process.exit(code ?? 1);
	await upload_directory(aws_sdet_bucket_name, full_test_reports_dir, s3_test_reports_dir);
	process.exit(code ?? 1);
};
