import { Cards } from "../client/component/cards.js";

export const cards_filters_change = async (page) => {
	try {
		await page.goto("http://localhost:3000", { timeout: 3000 });

		const cards = new Cards(page);
		await cards.click_filters_option("environment", "all");
		await cards.click_filters_option("day", "30");
		await cards.click_filters_option("app", "all");
		await cards.click_filters_option("protocol", "all");

		const card_count = await cards.get_card_count();
		console.log(`Cards displayed after applying filters: ${card_count}`);
	} catch (error) {
		const random_num = Math.floor(Math.random() * 10000);
		await page.screenshot({ path: `./screenshots/cards_error_${random_num}.png` });
		console.error(`Error in cards_filters_change. screenshot saved as: cards_error_${random_num}.png\n`, error);
		throw error;
	}
};
