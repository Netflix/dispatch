import register from "./utils/register"
import { test, expect } from "./fixtures/dispatch-fixtures"

test.describe("Authenticated Dispatch App", () => {
  test.beforeEach(async ({ authPage }) => {
    await register(authPage)
  }),
    test("Should allow me to report an case", async ({ page, reportCasePage }) => {
      /* The ability to report a case is one of the most critical
      user stories in the Dispatch application. */

      const title = "Case Test Created by Playwright"
      const description = "Test description created by Playwright"
      const project = "default"
      const type = "Security Triage"
      const priority = "Low"

      await reportCasePage.reportCase(title, description, project, type, priority)
      // Soft validate that we get redirected to the case submission form
      const expectedURL = encodeURI(
        `/default/cases/report?project=${project}&case_priority=${priority}&case_type=${type}&title=${title}&description=${description}`
      )
      // replace + with %20
      const pageURL = page.url().replace(/\+/g, "%20")

      await expect.soft(pageURL).toContain(expectedURL)

      // Soft validate that we receive the report form.
      await expect
        .soft(
          page.getByText("Open a Case"),
          "'Open a Case' text not visible on page after submission of a case."
        )
        .toBeVisible()

      // Soft validate that we receive the post-create resources form.
      await expect
        .soft(
          page.getByText(
            "This page will be populated with case resources as they are created (if available). If you have any questions, please feel free to review the Frequently Asked Questions (FAQ) document linked below, and/or reach out to the listed assignee."
          ),
          "'Case Resources' text not visible on page after submission of a case."
        )
        .toBeVisible()

      // Soft validate that the ticket link is present
      const loc = page.getByRole('link', { name: 'Ticket Ticket for tracking purposes. It contains information and links to resources.' })
      await expect.soft(await loc.first().getAttribute("href")).toContain('default/cases/dispatch-default-default-')

    })
})
