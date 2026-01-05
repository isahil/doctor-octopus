import { Cards } from "../client/component/cards.js";

export const cards_filters_change = async (page) => {
	const { TEST_REPORTS_DIR } = process.env;
	const random_num = Math.ceil(Math.random() * 3);
	console.log(`random_num for this run: ${random_num}`);
	try {
		await page.goto("http://localhost:3000", { timeout: 3000 });

		const cards = new Cards(page);
		await cards.click_filters_option("environment", "all");
		await cards.click_filters_option("day", "30");
		await cards.click_filters_option("app", "all");
		await cards.click_filters_option("protocol", "all");

		const card_count = await cards.get_card_count();
		console.log(`Cards displayed after applying filters: ${card_count}`);
		if (random_num == 2) {
			throw new Error("Simulated error for testing screenshot capture.");
		}
	} catch (error) {
		const new_random_num = Math.ceil(Math.random() * 10000);
		await page.screenshot({
			path: `${TEST_REPORTS_DIR}/screenshots/cards_error_${new_random_num}.png`,
		});
		console.error(
			`Error in cards_filters_change. screenshot saved as: cards_error_${new_random_num}.png\n`,
			error
		);
		throw error;
	}
};
