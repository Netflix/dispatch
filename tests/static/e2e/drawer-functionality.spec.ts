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

    // Click on the kebab menu (three dots) for the first incident
    const firstIncidentKebab = page.locator("tr").nth(1).getByRole("button").nth(2)
    await firstIncidentKebab.click()

    // Click on "View / Edit" option
    const viewEditOption = page.getByText("View / Edit", { exact: true })
    await viewEditOption.click()

    // Wait for the drawer to open and be visible
    const drawer = page.locator(".v-navigation-drawer").first()
    await expect(drawer).toBeVisible()

    // Test making a change in the drawer
    // Navigate to the Details tab
    const detailsTab = page.getByRole("tab", { name: "Details" })
    await detailsTab.click()

    // Find and update the description field using label - get the first one (textarea)
    const descriptionField = page.getByLabel("Description", { exact: false }).first()

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
})
