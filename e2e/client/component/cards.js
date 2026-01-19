export class Cards {
	page;
	constructor(page) {
		this.page = page;
	}

	filter_locator(filter) {
		return this.page.locator(`//div[@class="${filter}-filters-wrapper"]`, {
			timeout: 3000,
		});
	}

	async click_filter(filter) {
		const filter_locator = this.filter_locator(filter);
		await filter_locator.click();
		return filter_locator;
	}

	async click_filters_option(filter, option) {
		const filter_locator = await this.click_filter(filter);
		const option_locator = filter_locator.getByText(option, { exact: true });
		await option_locator.click();
	}

	async get_cards_count() {
		return await this.page.locator(".card", { timeout: 3000 }).count();
	}
}
