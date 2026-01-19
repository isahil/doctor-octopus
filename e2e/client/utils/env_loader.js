import dotenv from "dotenv";
dotenv.config({ path: [".env", "../.env"] });
import { get_est_date_time } from "./index.js";
import { ensure_dir } from "./fs_helper.js";

export const get_client_url = () => {
	const { VITE_MAIN_SERVER_HOST, VITE_MAIN_SERVER_PORT } = process.env;
	return `http://${VITE_MAIN_SERVER_HOST}:${VITE_MAIN_SERVER_PORT}`;
}

export const get_environment = () => {
	const { ENVIRONMENT = "qa" } = process.env;
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
	const dir_exists = process.env["TEST_REPORTS_DIR"];
	if (dir_exists) {
		return dir_exists;
	}

	const report_dir = `${get_est_date_time()}`;
	const full_test_reports_dir = `./${test_reports_dir}/${report_dir}`;

	ensure_dir(full_test_reports_dir);
	process.env["TEST_REPORTS_DIR"] = full_test_reports_dir;
	console.log(`Ensured reports directory at: ${full_test_reports_dir}`);

	return full_test_reports_dir; // ./test_reports/1-2-2026_3-42-21_PM/
};

export const get_db_username = () => {
	const { DB_USER } = process.env;
	return DB_USER;
};

export const get_db_password = () => {
	const { DB_PASSWORD } = process.env;
	return DB_PASSWORD;
};

export const get_db_host = () => {
	const { DB_HOST } = process.env;
	return DB_HOST;
};

export const get_db_port = () => {
	const { DB_PORT } = process.env;
	return DB_PORT;
};

export const get_db_name = () => {
	const { DB_NAME } = process.env;
	return DB_NAME;
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
	const { GITHUB_ACTOR = "imran.sahil" } = process.env;
	return GITHUB_ACTOR;
};

/**
 * Get debug mode from environment variables.
 * - ACTIONS_STEP_DEBUG is set to "1" (GitHub Actions)
 * - RUNNER_DEBUG is set to "1" (GitHub Actions)
 * @returns Returns True if any of the above conditions are met, otherwise False.
 */
export const gh_actions_debug_mode = () => {
	return process.env["ACTIONS_STEP_DEBUG"] === "1" || process.env["RUNNER_DEBUG"] === "1";
};

export const get_artillery_cloud_api_key = () => {
	const { ARTILLERY_CLOUD_API_KEY } = process.env;
	return ARTILLERY_CLOUD_API_KEY;
};

export const artillery_record_mode = () => {
	const { ARTILLERY_RECORD_MODE = "false" } = process.env;
	return ARTILLERY_RECORD_MODE.toLowerCase() === "true";
};
