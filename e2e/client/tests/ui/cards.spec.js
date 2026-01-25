import { test, expect } from "playwright/test";
import { Cards } from "../../component";

test.describe("Doctor Octopus Reports Page UI Test", () => {
	test("Cards Component UI Validation", async ({ page }) => {
		const { step } = test;
		const cards = new Cards(page);

		await step("Navigate to Doctor Octopus", async () => {
			await page.goto("/");
		});

		await step("Verify Filters visibility", async () => {
			const environment_filter = cards.filter_locator("environment");
			await expect
				.soft(environment_filter, "Environment filter should be visible")
				.toBeVisible();

			const day_filter = cards.filter_locator("day");
			await expect.soft(day_filter, "Day filter should be visible").toBeVisible();

			const product_filter = cards.filter_locator("product");
			await expect.soft(product_filter, "Product filter should be visible").toBeVisible();

			const protocol_filter = cards.filter_locator("protocol");
			await expect.soft(protocol_filter, "Protocol filter should be visible").toBeVisible();
		});

		await step("Apply Filters and verify results", async () => {
			await cards.click_filters_option("environment", "all");
			await cards.click_filters_option("day", "30");
			await cards.click_filters_option("product", "all");
			await cards.click_filters_option("protocol", "all");

			await expect.soft(page.locator(".card").first()).toBeVisible();
			const card_count = await cards.get_cards_count();
			expect
				.soft(card_count, "There should be some cards displayed after applying filters")
				.toBeGreaterThan(0);
		});
	});
});
