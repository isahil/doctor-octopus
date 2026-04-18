export class Lab {
    page;
    constructor(page) {
        this.page = page;
    }

    component_locator(name) {
        return this.page.locator(`.${name}`);
    }
}