import { expect, test } from "playwright/test"

test.describe("Dummy Test Suite", () => {
  test("Google Test Pass", async ({ page }) => {
    await page.goto("https://www.google.com/")
    // setTimeout(() => {}, 3000);
    expect(await page.title()).toBe("Google")
  })

  // test("Google Test Fail", async ({ page }) => {
  //   await page.goto("https://www.apple.com/");
  //   expect(await page.title()).toBe("Google");
  // });

  const numbers = [1, 2, 3]

  test("Test Random 1", async () => {
    expect(numbers[Math.floor(Math.random() * numbers.length)]).toBe(1)
  })

  // test("Test Random 2", async () => {
  //   expect(numbers[Math.floor(Math.random() * numbers.length)]).toBe(2);
  // });

  test.skip("Skipped Test", async () => {
    expect(true).toBe(false)
  })
})
