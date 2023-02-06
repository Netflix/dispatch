import { test, expect } from "./fixtures/dispatch-fixtures"
import register from "./utils/register"

test.describe("Authenticated Dispatch App", () => {
  test.beforeEach(async ({ authPage }) => {
    await register(authPage)
  }),
    test("The edit list should appear after clicking the incident edit kebab.", async ({
      incidentsPage,
    }) => {
      await incidentsPage.goto()
      await incidentsPage.EditKebab.click()
      await expect(incidentsPage.EditMenu).toBeVisible()
      await expect.soft(incidentsPage.EditMenu).toBeVisible()
      await expect.soft(incidentsPage.EditViewEdit).toBeVisible()
      await expect.soft(incidentsPage.EditCreateReport).toBeVisible()
      await expect.soft(incidentsPage.EditRunWorkflow).toBeVisible()
      await expect.soft(incidentsPage.EditDelete).toBeVisible()
    })
})
