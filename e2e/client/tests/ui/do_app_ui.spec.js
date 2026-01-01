import { test, expect } from "playwright/test";
import { Cards, Lab } from "../../component";

test("Doctor Octopus UI Test", async ({ page }) => {
	const { step } = test;
	const cards = new Cards(page);

	await step("Navigate to the application", async () => {
		await page.goto("http://localhost:3000/");
	});

	await step("Verify Filters visibility", async () => {
		const environment_filter = cards.filter_locator("environment");
		await expect.soft(environment_filter, "Environment filter should be visible").toBeVisible();

		const day_filter = cards.filter_locator("day");
		await expect.soft(day_filter, "Day filter should be visible").toBeVisible();

		const product_filter = cards.filter_locator("app");
		await expect.soft(product_filter, "Product filter should be visible").toBeVisible();

		const protocol_filter = cards.filter_locator("protocol");
		await expect.soft(protocol_filter, "Protocol filter should be visible").toBeVisible();
	});

	await step("Apply Filters and verify results", async () => {
		await cards.click_filters_option("environment", "all");
		await cards.click_filters_option("day", "30");
		await cards.click_filters_option("app", "all");
		await cards.click_filters_option("protocol", "all");

		await expect.soft(page.locator(".card").first()).toBeVisible();
    const card_count = await cards.get_card_count();
    await expect.soft(card_count, "There should be some cards displayed after applying filters").toBeGreaterThan(0);
	});

	await step("Header snapshot verification", async () => {
		await expect.soft(page.getByRole("banner"), "Header banner should match ARIA snapshot").toMatchAriaSnapshot(`
    - heading "Doctor Octopus" [level=1]
    - navigation:
      - link "👩🏻‍🔬 Reports":
        - /url: /
      - link "🧪 Lab":
        - /url: /the-lab
      - link "GitHub Actions":
        - /url: https://github.com/isahil/doctor-octopus/actions
        - img
      - link "Grafana Dashboard":
        - /url: test
        - img "Grafana Icon"
    `);
	});

	await step("Navigate to the Lab page and verify contents", async () => {
		await page.getByRole("link", { name: "🧪 Lab" }).click();

    const lab = new Lab(page);

    const fix_me = lab.component_locator("fixme");
    await expect.soft(fix_me, "FixMe component should be visible").toBeVisible();

    const terminal_locator = lab.component_locator("terminal");
    await expect.soft(terminal_locator, "Terminal component should be visible").toBeVisible();

    const the_lab_locator = lab.component_locator("lab");
    await expect.soft(the_lab_locator, "Lab component should be visible").toBeVisible();
	});
});
