import { Cards } from "../client/component/cards.js";

const change_filter = async (cards, filter_name, filter_value, events) => {
	await cards.click_filters_option(filter_name, filter_value);
	events.emit("counter", "filters_changed", 1);
	events.emit("rate", "filters_change_rate");
};

export const cards_filters_change = async (page, context, events) => {
	const { TEST_REPORTS_DIR } = process.env;

	try {
		const start_time = performance.now();

		await page.goto("http://localhost:3000", { timeout: 3000 });

		const cards = new Cards(page);
		await change_filter(cards, "environment", "all", events);
		await change_filter(cards, "day", "30", events);
		await change_filter(cards, "product", "all", events);
		await change_filter(cards, "protocol", "all", events);

		const cards_count = await cards.get_cards_count();

		const end_time = performance.now();
		const duration = end_time - start_time;

		console.log(`cards_filters_change duration: ${duration} ms`);
		console.log(`Cards displayed after applying filters: ${cards_count}`);
		// const random_num = Math.ceil(Math.random() * 3);
		// if (random_num == 2) throw new Error("Simulated error for testing screenshot capture.");

		events.emit("histogram", "cards_count", cards_count);
		
	} catch (error) {
		events.emit("counter", "error_occurred", 1);
		const new_random_num = Math.ceil(Math.random() * 10000);
		await page.screenshot({
			path: `${TEST_REPORTS_DIR}/screenshots/cards_error_${new_random_num}.png`,
		});
		console.error(
			`Error in cards_filters_change. screenshot saved as: cards_error_${new_random_num}.png\n`,
			error,
		);
		throw error;
	}
};
