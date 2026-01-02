import is_ci from "is-ci";
import {
	spawn_child_process,
	get_artillery_cloud_api_key,
	artillery_record_mode,
	get_github_actor,
    get_est_date_time,
    get_test_reports_dir,
    gh_actions_debug_mode,
    upload_report,
} from "../client/utils/index.js";

const test_name = process.argv[2];
const environment = process.argv[3];
const options = process.argv[4] || "{}";

const full_test_reports_dir = get_test_reports_dir();

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
	const script = test_name.split("/").pop()?.replace(".yml", "").replace(".yaml", "") || "na";
	const json_report = `${full_test_reports_dir}/${script}_report.json`;
	const upload_report_to_s3 = async (code) => {
		await upload_report(code, {
			test_suite: `perf:${script}`,
			json_report,
			full_test_reports_dir,
		});
	};

	let artillery_tags = tags ? `,${tags}` : ""; // Tags help with filtering & reporting in Artillery Cloud
	artillery_tags = is_ci
		? `--tags ci:true,env:${environment},actor:${actor},dev:imran,component:${script}${artillery_tags}`
		: `--tags actor:${actor}${artillery_tags}`;

	const artillery_record = record ? ` --record --key ${artillery_cloud_api_key}` : "";

	const debug_mode = gh_actions_debug_mode() ? (script == "cards" ? "DEBUG=http* " : "DEBUG=socketio ") : ""; // Enable Artillery debug mode for GitHub Actions runs when GH Actions debug is enabled. Will not impact LOG_LEVEL settings for processors.

	const command = `${debug_mode}npx artillery run --output ${json_report} ${test_name} -e ${environment} ${artillery_tags}${artillery_record}`;

	spawn_child_process(command, upload_report_to_s3);
};

execute_runner({ test_name, environment }).catch(
	(error) => {
		console.error(`Error executing performance test runner: ${error.message}`);
		process.exit(1);
	}
);
