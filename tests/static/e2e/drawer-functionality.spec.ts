import register from "./utils/register"
import { test, expect } from "./fixtures/dispatch-fixtures"

test.describe("Drawer Functionality", () => {
  test.beforeEach(async ({ authPage }) => {
    await register(authPage)
  })

  test("Should open incident drawer, make changes, and save", async ({ page, incidentsPage }) => {
    // Navigate to incidents page
    await incidentsPage.goto()

    // Wait for the incidents table to load
    await page.waitForSelector("table")

    // Click on the first incident row to open it
    const firstIncidentRow = page.locator("tr").nth(1) // Skip header row
    await firstIncidentRow.click()

    // Wait for the drawer to open and be visible
    const drawer = page.locator("v-navigation-drawer").first()
    await expect(drawer).toBeVisible()

    // Test making a change in the drawer
    // Navigate to the Details tab
    const detailsTab = page.getByRole("tab", { name: "Details" })
    await detailsTab.click()

    // Find and update a field (let's try to find a description field)
    const descriptionField = page
      .locator("textarea, input[type='text']")
      .filter({ hasText: "" })
      .first()
    if (await descriptionField.isVisible()) {
      await descriptionField.click()
      await descriptionField.fill("Test description updated by Playwright")
    }

    // Save the changes
    const saveButton = page.getByRole("button").filter({ hasText: "save" }).first()
    await saveButton.click()

    // Wait for save to complete (look for loading state to disappear)
    await page.waitForTimeout(1000)

    // Close the drawer
    const closeButton = page.getByRole("button").filter({ hasText: "close" }).first()
    await closeButton.click()

    // Wait for drawer to close
    await expect(drawer).not.toBeVisible()
  })

  test("Should test case drawer functionality", async ({ page, incidentsPage }) => {
    // Navigate to cases page (assuming there's a cases route)
    await page.goto("/default/cases")

    // Wait for the cases table to load
    await page.waitForSelector("table")

    // Click on the first case row to open it
    const firstCaseRow = page.locator("tr").nth(1) // Skip header row
    await firstCaseRow.click()

    // Wait for the drawer to open and be visible
    const drawer = page.locator("v-navigation-drawer").first()
    await expect(drawer).toBeVisible()

    // Close the drawer
    const closeButton = page.getByRole("button").filter({ hasText: "close" }).first()
    await closeButton.click()

    await expect(drawer).not.toBeVisible()
  })
})
