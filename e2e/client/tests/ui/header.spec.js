import { test, expect } from "playwright/test";

test.describe("Doctor Octopus Header UI Test", () => {
	test("Header UI Snapshot Validation", async ({ page }) => {
		const { step } = test;

		await step("Navigate to Doctor Octopus", async () => {
			await page.goto("/");
		});

		await step("Header snapshot verification", async () => {
			await expect.soft(page.getByRole("banner"), "Header banner should match ARIA snapshot")
				.toMatchAriaSnapshot(`
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
	});
});
