import register from "./utils/register"
import { test, expect } from "./fixtures/dispatch-fixtures"

test.describe("Drawer Functionality", () => {
  test.beforeEach(async ({ authPage }) => {
    await register(authPage)
  })

  test("Should open incident drawer", async ({ page, incidentsPage }) => {
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

    await page.waitForTimeout(1000)

    // Wait for the drawer to open and be visible
    const drawer = page.locator(".v-navigation-drawer").first()
    await expect(drawer).toBeVisible()

    // Test making a change in the drawer
    // Navigate to the Details tab
    const detailsTab = page.getByRole("tab", { name: "Details" })
    await detailsTab.click()
  })
})
