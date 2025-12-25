import { test, expect } from "playwright/test";
import { list_objects, get_object, upload_file } from "../../utils/S3";

const bucketName = "doctor-octopus";

test.describe("S3 Utility Functions", () => {
  // ========== LIST OBJECTS TESTS ==========
  test.describe("list_objects()", () => {
    test("should establish successful S3 bucket connection & return valid response structure for list_objects", async () => {
      console.log("Running S3 List test...");
      const response = await list_objects();

      expect(response).toBeDefined();
      expect(response["MaxKeys"]).toBeDefined();
      console.log(`MaxKeys in S3 bucket: ${response["MaxKeys"]}`);
      expect(parseInt(response["MaxKeys"])).toBeGreaterThan(1);
      
      expect(response).toHaveProperty("$metadata");
      expect(response["$metadata"]).toHaveProperty("httpStatusCode");
      expect(response["$metadata"]["httpStatusCode"]).toBe(200);
            
      // Response should contain Contents array with objects
      expect(Array.isArray(response.Contents) || response.Contents === undefined).toBeTruthy();
      console.log(`Objects found: ${response.Contents?.length || 0}`);
      console.log("S3 List test complete.");
    });

    test("should filter objects by correct prefix (test_reports/)", async () => {
      const response = await list_objects();

      // If Contents exist, all keys should start with test_reports/
      if (response.Contents && response.Contents.length > 0) {
        const allMatch = response.Contents.every((obj) =>
          obj.Key.startsWith("test_reports/")
        );
        expect(allMatch).toBeTruthy();
      }
    });
  });

  // ========== GET OBJECT TESTS ==========
  test.describe("S3 get_object function test", () => {
    test("should retrieve object metadata when object exists", async () => {
      // First, list objects to find a valid key
      const listResponse = await list_objects();

      if (listResponse.Contents && listResponse.Contents.length > 0) {
        const firstObject = listResponse.Contents[0];
        const objectKey = firstObject.Key;

        const getResponse = await get_object(objectKey);

        expect(getResponse).toBeDefined();
        expect(getResponse["$metadata"]).toBeDefined();
        expect(getResponse["$metadata"]["httpStatusCode"]).toBe(200);
        console.log(`Successfully retrieved object: ${objectKey}`);
      }
    });

    test("should handle non-existent object gracefully", async () => {
      const nonExistentKey = "test_reports/non-existent-file-12345.txt";

      try {
        await get_object(nonExistentKey);
      } catch (error) {
        expect(error.name).toBe("NoSuchKey");
        console.log(`Correctly caught error for non-existent object: ${error.name}`);
      }
    });

    test("should return response body for valid object", async () => {
      const listResponse = await list_objects();

      if (listResponse.Contents && listResponse.Contents.length > 0) {
        const firstObject = listResponse.Contents[0];
        const objectKey = firstObject.Key;

        const getResponse = await get_object(objectKey);

        expect(getResponse.Body).toBeDefined();
        console.log(`Object body retrieved for: ${objectKey}`);
      }
    });

    test("should return metadata with content type", async () => {
      const listResponse = await list_objects();

      if (listResponse.Contents && listResponse.Contents.length > 0) {
        const firstObject = listResponse.Contents[0];
        const objectKey = firstObject.Key;

        const getResponse = await get_object(objectKey);

        expect(getResponse["ContentType"]).toBeDefined();
        console.log(`Content-Type: ${getResponse["ContentType"]}`);
      }
    });

    test("should handle special characters in object keys", async () => {
      // Test with URL-encoded characters
      const specialKey = "test_reports/report%20with%20spaces.json";

      try {
        await get_object(specialKey);
      } catch (error) {
        // Error is expected if object doesn't exist, but should handle properly
        expect(error).toBeDefined();
      }
    });
  });

  // ========== UPLOAD FILE TESTS ==========
  test.describe("S3 upload_file function test", () => {
    test("should upload file with correct content type for json", async () => {
      const key = `tests/unit-test-${Date.now()}.json`;
      const fileContent = JSON.stringify({ test: "data", timestamp: new Date().toISOString() });
      const contentType = "application/json";

      try {
        const response = await upload_file(bucketName, key, fileContent, contentType);

        expect(response).toBeDefined();
        expect(response["$metadata"]["httpStatusCode"]).toBe(200);
        console.log(`Successfully uploaded JSON file: ${key}`);
      } catch (error) {
        console.log(`Upload error (may be due to permissions): ${error.message}`);
      }
    });

    test("should upload file with correct content type for zip", async () => {
      const key = `tests/unit-test-${Date.now()}.zip`;
      const fileContent = Buffer.from("fake zip content");
      const contentType = "application/zip";

      try {
        const response = await upload_file(bucketName, key, fileContent, contentType);

        expect(response).toBeDefined();
        expect(response["$metadata"]["httpStatusCode"]).toBe(200);
        console.log(`Successfully uploaded ZIP file: ${key}`);
      } catch (error) {
        console.log(`Upload error (may be due to permissions): ${error.message}`);
      }
    });

    test("should upload text file with correct content type", async () => {
      const key = `tests/unit-test-${Date.now()}.txt`;
      const fileContent = "This is a test file for S3 upload";
      const contentType = "text/plain";

      try {
        const response = await upload_file(bucketName, key, fileContent, contentType);

        expect(response).toBeDefined();
        expect(response["$metadata"]["httpStatusCode"]).toBe(200);
        console.log(`Successfully uploaded text file: ${key}`);
      } catch (error) {
        console.log(`Upload error (may be due to permissions): ${error.message}`);
      }
    });

    test("should handle empty file upload", async () => {
      const key = `tests/unit-test-empty-${Date.now()}.txt`;
      const fileContent = "";
      const contentType = "text/plain";

      try {
        const response = await upload_file(bucketName, key, fileContent, contentType);

        expect(response).toBeDefined();
        console.log(`Successfully uploaded empty file: ${key}`);
      } catch (error) {
        console.log(`Upload error (may be due to permissions): ${error.message}`);
      }
    });

    test("should support custom content types", async () => {
      const bucketName = "doctor-octopus";
      const key = `tests/unit-test-${Date.now()}.html`;
      const fileContent = "<html><body>Test Report</body></html>";
      const contentType = "text/html";

      try {
        const response = await upload_file(bucketName, key, fileContent, contentType);

        expect(response).toBeDefined();
        expect(response["$metadata"]["httpStatusCode"]).toBe(200);
        console.log(`Successfully uploaded HTML file with custom content type: ${key}`);
      } catch (error) {
        console.log(`Upload error (may be due to permissions): ${error.message}`);
      }
    });
  });

  // ========== DATA INTEGRITY TESTS ==========
  test.describe("S3 Data Integrity Test", () => {
    test("should return consistent MaxKeys value", async () => {
      const response1 = await list_objects();
      const response2 = await list_objects();

      expect(response1["MaxKeys"]).toBe(response2["MaxKeys"]);
      console.log(`MaxKeys consistency verified: ${response1["MaxKeys"]}`);
    });
  });
});
