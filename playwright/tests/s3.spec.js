import { test, expect } from "playwright/test";
import { list_objects, upload_directory } from "../S3";
const { AWS_BUCKET_NAME, REPORTS_DIR } = process.env;

test("S3 List", async () => {
    console.log("Running S3 List test...")
    await list_objects()
    console.log("S3 List test complete.")
    expect(true).toBe(true)
});

test.skip("S3 Upload", async () => {
    console.log("Running S3 Upload test...")
    await upload_directory(AWS_BUCKET_NAME, `${REPORTS_DIR}/results_4`)
})