import { Cards } from "../client/component/cards.js";

export const cards_filters_change = async (page) => {
    await page.goto("http://localhost:3000", { timeout: 3000 });

	const cards = new Cards(page);
	await cards.click_filters_option("environment", "all");
	await cards.click_filters_option("day", "30");
	await cards.click_filters_option("app", "all");
	await cards.click_filters_option("protocol", "all");

	// await expect.soft(page.locator(".card").first()).toBeVisible();
	const card_count = await cards.get_card_count();
    console.log(`Cards displayed after applying filters: ${card_count}`);
};
