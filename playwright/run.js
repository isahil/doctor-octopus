import "dotenv/config";
import os from "os";
import fs from "fs";
import { execSync } from "child_process";
import { upload_directory } from "./S3.js";
import { spawn_child_process } from "./spawn_child_process.js";

const get_est_date_time = () => {
  const date = new Date();
  return `${date.getFullYear()}-${
    date.getMonth() + 1
  }-${date.getDate()}-${date.getHours()}-${date.getMinutes()}-${date.getSeconds()}`;
};

const { AWS_BUCKET_NAME } = process.env;
console.log(`AWS_BUCKET_NAME: ${AWS_BUCKET_NAME}`);
const test_script_name = process.argv[2];
const test_protocol = test_script_name.split(":")[0];

const reports_dir_name = `test_reports`;
const test_reports_dir_name = `${get_est_date_time()}`;
const local_test_reports_dir_path = `./${reports_dir_name}/${test_reports_dir_name}`;
const s3_test_reports_dir_path = `trading-apps/${reports_dir_name}/${test_protocol}/${test_reports_dir_name}`;

process.env.TEST_REPORTS_DIR = local_test_reports_dir_path;
const os_username = os.userInfo().username;
const git_branch = execSync("git rev-parse --abbrev-ref HEAD")
  .toString()
  .trim();
const report_card_path = `${local_test_reports_dir_path}/report.json`; // Read the report_card.json file to upload

const upload_report = async () => {
  const report_card = JSON.parse(fs.readFileSync(report_card_path, "utf-8"));
  // Add the git-branch & username to the report_card object
  report_card["stats"]["git_branch"] = git_branch;
  report_card["stats"]["username"] = os_username;

  // Write the updated reportCard object back to the report.json file
  fs.writeFileSync(report_card_path, JSON.stringify(report_card, null, 2));
  await upload_directory(
    AWS_BUCKET_NAME,
    local_test_reports_dir_path,
    s3_test_reports_dir_path
  );
};

// spawn_child_process(`npx playwright test --project=${test_script_name}`, upload_report)
spawn_child_process(`npx playwright test --project=${test_script_name}`)