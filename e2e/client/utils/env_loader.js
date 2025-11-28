import dotenv from "dotenv";
dotenv.config({ path: [".env", "../.env"] });
import is_ci from "is-ci";
import fs from "fs";
import { get_est_date_time } from "./index.js";

export const get_environment = () => {
	const { ENVIRONMENT } = process.env;
	return ENVIRONMENT;
};

export const get_product = () => {
	const { APP } = process.env;
	return APP ?? "loan";
};

export const get_app_name = () => {
	const { APP_NAME } = process.env;
	return APP_NAME ?? "trading-apps";
};

export const get_test_reports_dir = () => {
	const test_reports_dir = "test_reports";
	const report_dir = `${get_est_date_time()}`;
	const full_test_reports_dir = `./${test_reports_dir}/${report_dir}`;
	const dir_exists = process.env["TEST_REPORTS_DIR"];
	if (!dir_exists) {
		if (!fs.existsSync(full_test_reports_dir)) {
			fs.mkdirSync(full_test_reports_dir, { recursive: true });
		}
		process.env["TEST_REPORTS_DIR"] = full_test_reports_dir;
		console.log(`Created test reports directory at: ${full_test_reports_dir}`);
	}
	return full_test_reports_dir;
};

export const get_aws_sdet_bucket_name = () => {
	const { AWS_SDET_BUCKET_NAME } = process.env;
	return AWS_SDET_BUCKET_NAME;
};

export const get_aws_sdet_bucket_region = () => {
	const { AWS_SDET_BUCKET_REGION } = process.env;
	return AWS_SDET_BUCKET_REGION;
};

export const get_aws_sdet_bucket_access_key_id = () => {
	const { AWS_SDET_BUCKET_ACCESS_KEY_ID } = process.env;
	return AWS_SDET_BUCKET_ACCESS_KEY_ID;
};

export const get_aws_sdet_bucket_secret_access_key = () => {
	const { AWS_SDET_BUCKET_SECRET_ACCESS_KEY } = process.env;
	return AWS_SDET_BUCKET_SECRET_ACCESS_KEY;
};

export const get_github_run_id = () => {
	const { GITHUB_RUN_ID } = process.env;
	return GITHUB_RUN_ID;
};

export const get_github_repository = () => {
	const { GITHUB_REPOSITORY } = process.env;
	return GITHUB_REPOSITORY;
};

export const get_github_server_url = () => {
	const { GITHUB_SERVER_URL } = process.env;
	return GITHUB_SERVER_URL;
};

export const get_github_actor = () => {
	const { GITHUB_ACTOR } = process.env;
	return GITHUB_ACTOR;
};

export const gh_actions_debug_mode = () => {
	if (is_ci) return false;
	return process.env["ACTIONS_STEP_DEBUG"] === "1" || process.env["RUNNER_DEBUG"] === "1";
};
