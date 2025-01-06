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
const test_script_name = process.argv[2];
const test_protocol = test_script_name.split(":")[0];

const test_reports_dir = `test_reports`;
const report_dir = `${get_est_date_time()}`;
const local_test_reports_dir = `./${test_reports_dir}/${report_dir}`;
process.env.TEST_REPORTS_DIR = local_test_reports_dir;
const s3_test_reports_dir = `trading-apps/${test_reports_dir}/${test_protocol}/${report_dir}`;

const os_username = os.userInfo().username;
const git_branch = execSync("git rev-parse --abbrev-ref HEAD")
  .toString()
  .trim();
const report_card_path = `${local_test_reports_dir}/report.json`; // Read the report_card.json file to upload

const upload_report = async (code) => {
  const report_card = JSON.parse(fs.readFileSync(report_card_path, "utf-8"));
  // Add the git-branch & username to the report_card object
  report_card["stats"]["git_branch"] = git_branch;
  report_card["stats"]["username"] = os_username;

  // Write the updated reportCard object back to the report.json file
  fs.writeFileSync(report_card_path, JSON.stringify(report_card, null, 2));
  await upload_directory(
    AWS_BUCKET_NAME,
    local_test_reports_dir,
    s3_test_reports_dir
  );
  process.exit(code ?? 1);
};

// spawn_child_process(`npx playwright test --project=${test_script_name}`, upload_report)
spawn_child_process(`npx playwright test --project=${test_script_name}`)
