import is_ci from "is-ci";
import os from "os";
import fs from "fs";
import { execSync } from "child_process";
import {
	spawn_child_process,
	get_artillery_cloud_api_key,
	artillery_record_mode,
	get_environment,
	get_app_name,
	get_product,
	get_aws_sdet_bucket_name,
	get_github_run_id,
	get_github_repository,
	get_github_server_url,
	get_github_actor,
	get_est_date_time,
	get_test_reports_dir,
	gh_actions_debug_mode,
	upload_report,
} from "../client/utils/index.js";

const test_name = process.argv[2];
const environment = process.argv[3];
const options = process.argv[4] || "{}";

const product = get_product();
const app_name = get_app_name();
const test_protocol = test_name.split("/").pop()?.replace(".yml", "").replace(".yaml", "") || "na";
const test_suite = `perf:${test_protocol}`;
const test_reports_dir = "test_reports";
const runner = "perf/runner.js";

const full_test_reports_dir = get_test_reports_dir();
let json_report_path = "", script = "";

const upload_report_to_s3 = async (code) => {
	await upload_report(code, {
		test_suite: `perf:${script}`,
		json_report: json_report_path,
		full_test_reports_dir,
	});
};

const generate_report = () => {
	add_stats_to_json();
	console.log(`Generating HTML report from JSON: ${json_report_path} -> ${full_test_reports_dir}`);
	spawn_child_process(`npm run generate-haiku-report ${json_report_path} ${full_test_reports_dir}`, upload_report_to_s3);
};

const add_stats_to_json = () => {
	const report_card = JSON.parse(fs.readFileSync(json_report_path, "utf-8"));

	// Add meta data below
	const os_username = os.userInfo().username;
	const git_branch = execSync("git rev-parse --abbrev-ref HEAD").toString().trim();
	report_card["stats"] ??= {};
	report_card["stats"]["app"] = product;
	report_card["stats"]["app_name"] = app_name;
	report_card["stats"]["environment"] = environment;
	report_card["stats"]["git_branch"] = git_branch;
	report_card["stats"]["protocol"] = test_protocol;
	report_card["stats"]["product"] = product;
	report_card["stats"]["runner"] = runner;
	report_card["stats"]["test_reports_dir"] = test_reports_dir;
	report_card["stats"]["test_suite"] = test_suite;
	report_card["stats"]["username"] = os_username;

	if (is_ci) {
		const run_id = get_github_run_id(); // e.g., 1234567890
		const repo = get_github_repository(); // e.g., owner/repo
		const server = get_github_server_url() || "https://github.com";
		const run_url = run_id && repo ? `${server}/${repo}/actions/runs/${run_id}` : "na";
		const sdet = get_github_actor() || os_username;
		report_card["ci"] = { run_id, run_url, sdet };
	}

	// Write the updated report_card object back to the report.json file
	fs.writeFileSync(json_report_path, JSON.stringify(report_card, null, 2));
}

export const execute_runner = async ({ test_name, environment, tags }) => {
	const artillery_cloud_api_key = get_artillery_cloud_api_key();
	const record = artillery_record_mode();
	const actor = get_github_actor();

	if (!test_name || !environment) {
		throw new Error(`Required script arguments are missing! [${get_est_date_time()}]`);
	}

	console.log(
		`Starting... artillery test: [${test_name}] | environment: ${environment} | options: ${options ?? "{}"} | record-mode: ${record} [${get_est_date_time()}]`
	);
	script = test_name.split("/").pop()?.replace(".yml", "").replace(".yaml", "") || "na";
	json_report_path = `${full_test_reports_dir}/${script}_report.json`; // e.g., ./test_reports/1-2-2026_3-42-21_PM/cards_report.json
	
	let artillery_tags = tags ? `,${tags}` : ""; // Tags help with filtering & reporting in Artillery Cloud
	artillery_tags = is_ci
		? `--tags ci:true,env:${environment},actor:${actor},dev:imran,component:${script}${artillery_tags}`
		: `--tags actor:${actor}${artillery_tags}`;

	const artillery_record = record ? ` --record --key ${artillery_cloud_api_key}` : "";

	const debug_mode = gh_actions_debug_mode()
		? script == "cards"
			? "DEBUG=http* "
			: "DEBUG=socketio "
		: ""; // Enable Artillery debug mode for GitHub Actions runs when GH Actions debug is enabled. Will not impact LOG_LEVEL settings for processors.

	const command = `${debug_mode}npx artillery run --output ${json_report_path} ${test_name} -e ${environment} ${artillery_tags}${artillery_record}`;

	spawn_child_process(command, generate_report);
};

execute_runner({ test_name, environment }).catch((error) => {
	console.error(`Error executing performance test runner: ${error.message}`);
	process.exit(1);
});
