import register from "./utils/register"
import { test, expect } from "./fixtures/dispatch-fixtures"

test.describe("Authenticated Dispatch App", () => {
  test.beforeEach(async ({ authPage }) => {
    await register(authPage)
  }),
    test("Should allow me to report an event", async ({ page, reportEventPage }) => {
      /* The ability to report a case is one of the most critical
      user stories in the Dispatch application. */

      const description = "Security Event Test Created by Playwright"
      const title = "Security Event Triage"

      await reportEventPage.reportEvent(description)
      // Soft validate that we get redirected to the event submission form
      const expectedURL = encodeURI(
        `/default/events/report?project=default&title=${title}&description=${description}`
      )
      // replace + with %20
      const pageURL = page.url().replace(/\+/g, "%20")

      await expect.soft(pageURL).toContain(expectedURL)

      // Soft validate that we receive the post-create resources form.
      await expect
        .soft(
          page.getByText(
            "This page will be populated with case resources as they are created (if available). If you have any questions, please feel free to review the Frequently Asked Questions (FAQ) document linked below, and/or reach out to the listed assignee."
          ),
          "'Case Resources' text visible on page after submission of a case."
        )
        .toBeVisible()

      // Soft validate that the ticket link is present
      const loc = page.getByRole("link", {
        name: "Ticket Ticket for tracking purposes. It contains information and links to resources.",
      })
      await expect
        .soft(await loc.first().getAttribute("href"))
        .toContain("default/cases/dispatch-default-default-")
    }),
    test("Should allow me to report an event with urgent flagged", async ({
      page,
      reportEventPage,
    }) => {
      /* The ability to report a case is one of the most critical
      user stories in the Dispatch application. */

      const description = "Security Event Test Created by Playwright"
      const title = "Security Event Triage"

      await reportEventPage.reportEvent(description, true)
      // Soft validate that we get redirected to the case submission form
      const expectedURL = encodeURI(
        `/default/events/report?project=default&title=${title}&description=${description}`
      )
      // replace + with %20
      const pageURL = page.url().replace(/\+/g, "%20")

      await expect.soft(pageURL).toContain(expectedURL)

      // Soft validate that we receive the post-create resources form.
      await expect
        .soft(
          page.getByText(
            "This page will be populated with case resources as they are created (if available). If you have any questions, please feel free to review the Frequently Asked Questions (FAQ) document linked below, and/or reach out to the listed assignee."
          ),
          "'Case Resources' text visible on page after submission of an event."
        )
        .toBeVisible()

      // Validate that the Priority is set to 'Critical'
      const priorityElement = page.getByText("Priority")

      const subtitleElement = priorityElement.locator(
        'xpath=following-sibling::div[contains(@class, "v-list-item-subtitle")]'
      )
      await expect(subtitleElement).toBeVisible()
      await expect(subtitleElement).toHaveText(/Critical/)

      // Soft validate that the ticket link is present
      const loc = page.getByRole("link", {
        name: "Ticket Ticket for tracking purposes. It contains information and links to resources.",
      })
      await expect
        .soft(await loc.first().getAttribute("href"))
        .toContain("default/cases/dispatch-default-default-")
    })
})
