import { test, expect } from "playwright/test";
import sql from "../../utils/postgre_sql";
import { fs_parse_csv } from "../../utils/fs_helper";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const csv_data_path = path.join(__dirname, "Electric_Vehicle_Population_Data.csv");

const integer_fields = ["model_year", "electric_range", "base_msrp", "legislative_district", "dol_vehicle_id"];
const float_fields = ["census_tract_2020"];

const sanitizeRecord = (record) => {
  const cleaned = {};
  for (const [key, value] of Object.entries(record)) {
    if (value === "" || value === undefined) {
      cleaned[key] = null;
      continue;
    }
    if (integer_fields.includes(key)) {
      const parsed = parseInt(value, 10);
      cleaned[key] = Number.isFinite(parsed) ? parsed : null;
      continue;
    }
    if (float_fields.includes(key)) {
      const parsed = parseFloat(value);
      cleaned[key] = Number.isFinite(parsed) ? parsed : null;
      continue;
    }
    cleaned[key] = value;
  }
  return cleaned;
};

test.describe("Database Tests", () => {
  test("Connect to PostgreSQL and run a simple query", async () => {
    const result = await sql`SELECT * FROM electric_vehicle LIMIT 5;`;
    console.log("DB Query Result before INSERT sample:", JSON.stringify(result));
    expect(Array.isArray(result)).toBeTruthy();
    expect(result.length).toBeLessThanOrEqual(5);
  });

  test("Validate data from CSV file", async () => {
    const records = fs_parse_csv(csv_data_path);
    console.log(`CSV Records total: ${records.length}`);
    expect(records.length).toBeGreaterThan(0);
    expect(records[0]).toHaveProperty("make");
    expect(records[0]).toHaveProperty("model");
  });

  test("Insert CSV data into PostgreSQL and verify", async () => {
    const cleanedRecords = fs_parse_csv(csv_data_path).map(sanitizeRecord);
    console.log(`Inserting ${cleanedRecords.length} sanitized records into the database...`);

    const batchSize = 300;
    await sql.begin(async (tx) => {
      for (let i = 0; i < cleanedRecords.length; i += batchSize) {
        const batch = cleanedRecords.slice(i, i + batchSize);
        await tx`INSERT INTO electric_vehicle ${sql(batch)}`;
        console.log(`Inserted batch: ${i + batch.length}/${cleanedRecords.length}`);
      }
    });

    console.log("Data insertion completed.");

    const [{ count }] = await sql`SELECT COUNT(*)::int AS count FROM electric_vehicle;`;
    console.log(`Total records in electric_vehicle table after insertion: ${count}`);
    expect(count).toBeGreaterThanOrEqual(cleanedRecords.length);
  });
});