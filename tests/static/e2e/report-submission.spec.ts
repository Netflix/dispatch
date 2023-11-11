import register from "./utils/register"
import { test, expect } from "./fixtures/dispatch-fixtures"

test.describe("Authenticated Dispatch App", () => {
  test.beforeEach(async ({ authPage }) => {
    await register(authPage)
  }),
    test("Should allow me to report an incident", async ({ page, reportIncidentPage }) => {
      /* The ability to report an incident is one of the most critical
      user stories in the Dispatch application. */

      const title = "Incident Test Created by Playwright"
      const description = "Test description created by Playwright"
      const project = "default"
      const type = "Denial of Service"
      const priority = "Low"
      const tags = ["ExampleTag"]

      await reportIncidentPage.reportIncident(title, description, project, type, priority, tags)
      // Soft validate that we get redirected to the incident submission form
      let expectedURL = encodeURI(
        `/default/incidents/report?project=${project}&incident_priority=${priority}&incident_type=${type}&title=${title}&description=${description}` + tags.map((tag) => "&tag=" + tag).join("")
      )
      // replace + with %20
      let pageURL = page.url().replace(/\+/g, "%20")

      await expect.soft(pageURL).toContain(expectedURL)

      // Soft validate that we recieve the report form.
      await expect
        .soft(
          page.getByText("Incident Report"),
          "'Incident Report' text not visible on page after submission of incident report."
        )
        .toBeVisible()

      // Soft validate that we recieve the report form.
      await expect
        .soft(
          page.getByText(
            "This page will be populated with incident resources as they are created (if available). If you have any questions, please feel free to review the Frequently Asked Questions (FAQ) document linked below, and/or reach out to the listed Incident Commander."
          ),
          "'Incident Report: Description' not visible on page after submission of incident report."
        )
        .toBeVisible()
    }),
    test("The 'Load More' selector should be visible when there are more than 5 options in Type combobox.", async ({
      reportIncidentPage,
    }) => {
      await reportIncidentPage.goto()
      await reportIncidentPage.typeDropdown.click()

      // Soft check that the 'Load More' selector is available upon opening the Project dropdown
      await expect
        .soft(
          reportIncidentPage.loadMore,
          "The 'Load More' selector should be visible when there are more than 5 options in Type combobox."
        )
        .toBeVisible()
    })
})
