import { test, expect } from "playwright/test";
import { Cards, Lab } from "../../component";

test.describe("Doctor Octopus Lab Page UI Test", () => {
	test("Lab UI Validation", async ({ page }) => {
		const { step } = test;

		await step("Navigate to Doctor Octopus", async () => {
			await page.goto("/");
		});

		await step("Navigate to the Lab page and verify contents", async () => {
			await page.getByRole("link", { name: "🧪 Lab" }).click();

			const lab = new Lab(page);

			const fix_me = lab.component_locator("fixme");
			await expect.soft(fix_me, "FixMe component should be visible").toBeVisible();

			const terminal_locator = lab.component_locator("terminal");
			await expect
				.soft(terminal_locator, "Terminal component should be visible")
				.toBeVisible();

			const the_lab_locator = lab.component_locator("lab");
			await expect.soft(the_lab_locator, "Lab component should be visible").toBeVisible();
		});
	});
});
