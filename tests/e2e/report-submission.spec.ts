import { test, expect, chromium } from "@playwright/test"
import login from "./utils/login"

test.describe("Authenticated Dispatch App", () => {
  test.beforeEach(async ({ page }) => {
    await login(page)
  })
  test("Should allow me to report an incident", async ({ page }) => {
    /* The ability to report an incident is one of the most critical
      user stories in the Dispatch application. */

    const project = "Test"
    const type = "Customer Data"
    const priority = "Low"

    await page.getByRole("link", { name: "Report Incident" }).click()

    // Title
    await page.getByLabel("Title").click()
    await page.getByLabel("Title").fill("Incident Test Created by Playwright")

    // Description
    await page.getByLabel("Description").click()
    await page.getByLabel("Description").fill("test")

    // Project
    await page.getByRole("combobox").filter({ hasText: "Project" }).locator("i").click()
    await page.getByText(project, { exact: true }).click()

    // Type
    await page.getByRole("button", { name: "Type" }).click()
    await page.getByText(type, { exact: true }).click()

    // Priority
    await page.getByRole("button", { name: "Priority" }).click()
    await page.getByText(priority).click()

    // Open the dropdown selection for the Tags field
    await page.getByRole("combobox").filter({ hasText: "Tags" }).locator("i").click()

    // Soft check that the 'Load More' selector is available upon opening the Tags dropdown
    await expect
      .soft(page.getByText("Load More"), "The 'Load More' selector should be visibile.")
      .toBeVisible()

    // Click load more
    await page.getByText("Load More").click()

    // Submit the form
    await page.getByRole("button", { name: "Submit" }).click()

    // Wait for the incident to be created
    await page.waitForLoadState("networkidle")

    // Soft validate that we get redirected to the incident submission form
    await expect
      .soft(page)
      .toHaveURL(
        encodeURI(
          `./default/incidents/report?project=${project}&incident_priority=${priority}&incident_type=${type}`
        )
      )

    // Soft validate that we recieve the report form.
    await expect.soft(page.getByText("Incident Report")).toBeVisible()

    // Soft validate that we recieve the report form.
    await expect
      .soft(
        page.getByText(
          "This page will be populated with incident resources as they are created (if available). If you have any questions, please feel free to review the Frequently Asked Questions (FAQ) document linked below, and/or reach out to the listed Incident Commander."
        )
      )
      .toBeVisible()
  })
})
