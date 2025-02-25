import "dotenv/config"
import CI from "is-ci"
import os from "os"
import fs from "fs"
import { execSync } from "child_process"
import { get_est_date_time, spawn_child_process, upload_directory } from "./index.js"

const { AWS_SDET_BUCKET_NAME, ENVIRONMENT, PRODUCT_TYPE, APP } = process.env
const test_script_name = process.argv[2]
const test_protocol = test_script_name.split(":")[0]

const test_reports_dir = "test_reports"
const report_dir = `${get_est_date_time()}`
const local_test_reports_dir = `./${test_reports_dir}/${report_dir}`
process.env.TEST_REPORTS_DIR = local_test_reports_dir
const s3_test_reports_dir = `trading-apps/${test_reports_dir}/${test_protocol}/${report_dir}`

const os_username = os.userInfo().username
const git_branch = execSync("git rev-parse --abbrev-ref HEAD").toString().trim()
const json_report = `${local_test_reports_dir}/report.json` // Need to read the report_card.json file to upload

const upload_report = async (code) => {
  const report_card = JSON.parse(fs.readFileSync(json_report, "utf-8"))

  // Add the git-branch & username to the report_card object
  report_card["stats"]["git_branch"] = git_branch
  report_card["stats"]["username"] = os_username
  report_card["stats"]["environment"] = ENVIRONMENT
  report_card["stats"]["app"] = PRODUCT_TYPE ? PRODUCT_TYPE : APP
  report_card["stats"]["test_suite"] = test_script_name

  // Write the updated reportCard object back to the report.json file
  fs.writeFileSync(json_report, JSON.stringify(report_card, null, 2))
  console.log(`Uploading test reports to S3 bucket: ${AWS_SDET_BUCKET_NAME}`)
  if(CI) await upload_directory(AWS_SDET_BUCKET_NAME, local_test_reports_dir, s3_test_reports_dir)
  process.exit(code ?? 1)
}

spawn_child_process(`npx playwright test --project=${test_script_name}`, upload_report)
