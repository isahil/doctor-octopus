import { test, expect } from "playwright/test"
import { list_objects } from "../S3"

test("S3 Bucket Connection Test", async () => {
  console.log("Running S3 List test...")
  const total_objects = await list_objects()
  console.log(`Total objects in S3 bucket: ${total_objects}`)
  expect(total_objects).toBeGreaterThan(1)
  console.log("S3 List test complete.")
})
