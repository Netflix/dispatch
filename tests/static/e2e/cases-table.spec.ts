import { test, expect } from "./fixtures/dispatch-fixtures"
import register from "./utils/register"

test.describe("CaseTable", () => {
  test.beforeEach(async ({ authPage }) => {
    await register(authPage)
  }),
    test("The edit list should appear after clicking the case edit kebab.", async ({
      casesPage,
    }) => {
      await casesPage.goto()
      await casesPage.EditKebab.click()
      await expect(casesPage.EditMenu).toBeVisible()
      await expect.soft(casesPage.EditViewEdit).toBeVisible()
      await expect.soft(casesPage.EditDelete).toBeVisible()
    })
})
