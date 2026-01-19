import { Cards } from "../client/component/cards.js";

const homepage_url = "http://localhost:3000";

const change_filter = async (cards, filter_name, filter_value, events) => {
	await cards.click_filters_option(filter_name, filter_value);
	events.emit("counter", "filters_changed", 1);
	events.emit("rate", "filters_change_rate");
};

export const cards_filters_change = async (page, context, events, test) => {
	const { step } = test;
	const { TEST_REPORTS_DIR } = process.env;

	try {
		const start_time = performance.now();

		await step("Navigate to homepage", async () => {
			await page.goto(homepage_url, { timeout: 3000 });
		});

		const cards = new Cards(page);

		await step("Apply filters", async () => {
			await change_filter(cards, "environment", "all", events);
			await change_filter(cards, "day", "30", events);
			await change_filter(cards, "product", "all", events);
			await change_filter(cards, "protocol", "all", events);
		});

		await step("Verify cards loaded", async () => {
			const cards_count = await cards.get_cards_count();
			if (cards_count === 0) {
				throw new Error("No cards displayed after applying filters.");
			}

			const end_time = performance.now();
			const duration = end_time - start_time;
			// console.log(`cards_filters_change duration: ${duration} ms`);
			// console.log(`Cards displayed after applying filters: ${cards_count}`);

			events.emit("histogram", "cards_filter_change_duration", duration);
		});
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
