import is_ci from "is-ci";
import {
	spawn_child_process,
	get_artillery_cloud_api_key,
	artillery_record_mode,
	add_stats_to_json,
	get_github_actor,
	get_est_date_time,
	get_test_reports_dir,
	gh_actions_debug_mode,
	upload_report,
} from "../client/utils/index.js";

let test_suite = process.argv[2];
const environment = process.argv[3];
const options = process.argv[4] || "{}";

const full_test_reports_dir = get_test_reports_dir();
let json_report_path = "", feature = "";

const upload_report_to_s3 = async (code) => {
	try {
		await upload_report(code, {
			test_suite,
			full_test_reports_dir,
		});
		process.exit(code || 0); // Exit with test code or 0
	} catch (error) {
		console.error(`Error uploading report: ${error.message}`);
		process.exit(1);
	}
};

const generate_reports = (code) => {
	test_suite = `perf:${feature}`
	console.log(`Received test completion code from the last process: ${code}`);
	add_stats_to_json({ test_suite, json_report_path, runner: "artillery" });
	console.log(
		`Generating HTML report from JSON: ${json_report_path} -> ${full_test_reports_dir}`
	);

	spawn_child_process(
		`npm run generate-haiku-report ${json_report_path} ${full_test_reports_dir}`,
		upload_report_to_s3
	);
};

export const execute_runner = async ({ test_suite, environment, tags }) => {
	const artillery_cloud_api_key = get_artillery_cloud_api_key();
	const record = artillery_record_mode();
	const actor = get_github_actor();

	if (!test_suite || !environment) {
		throw new Error(`Required script arguments are missing! [${get_est_date_time()}]`);
	}

	console.log(
		`Starting... artillery test: [${test_suite}] | environment: ${environment} | options: ${options ?? "{}"} | record-mode: ${record} [${get_est_date_time()}]`
	);
	feature = test_suite.split("/").pop()?.replace(".yml", "").replace(".yaml", "") || "na";
	json_report_path = `${full_test_reports_dir}/${feature}_report.json`; // e.g., ./test_reports/1-2-2026_3-42-21_PM/cards_report.json

	let artillery_tags = tags ? `,${tags}` : ""; // Tags help with filtering & reporting in Artillery Cloud
	artillery_tags = is_ci
		? `--tags ci:true,env:${environment},actor:${actor},dev:imran,component:${feature}${artillery_tags}`
		: `--tags actor:${actor}${artillery_tags}`;

	const artillery_record = record ? ` --record --key ${artillery_cloud_api_key}` : "";

	const debug_mode = gh_actions_debug_mode()
		? feature == "cards"
			? "DEBUG=http* "
			: "DEBUG=socketio "
		: ""; // Enable Artillery debug mode for GitHub Actions runs when GH Actions debug is enabled. Will not impact LOG_LEVEL settings for processors.

	const command = `${debug_mode}npx artillery run --output ${json_report_path} ${test_suite} -e ${environment} --variables '{"test_reports_dir":"${full_test_reports_dir}"}' ${artillery_tags}${artillery_record}`;

	spawn_child_process(command, generate_reports);
};

execute_runner({ test_suite, environment }).catch((error) => {
	console.error(`Error executing performance test runner: ${error.message}`);
	process.exit(1);
});
