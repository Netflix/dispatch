import register from "./utils/register"
import { test, expect } from "./fixtures/dispatch-fixtures"

test.describe("Authenticated Dispatch App", () => {
  test.beforeEach(async ({ authPage }) => {
    await register(authPage)
  }),
    test("Should allow me to report a case", async ({ page, reportCasePage }) => {
      /* The ability to report an incident is one of the most critical
      user stories in the Dispatch application. */

      const title = "Case Test Created by Playwright"
      const description = "Test description created by Playwright"
      const project = "default"

      await reportCasePage.reportCase(title, description, project)
      // Soft validate that we get redirected to the incident submission form
      await expect
        .soft(page)
        .toHaveURL(
          encodeURI(
            `./default/cases/report?project=${project}`
          )
        )

      // Soft validate that we recieve the report form.
      await expect
        .soft(
          page.getByText("Case Report"),
          "'Case Report' text not visible on page after submission of case report."
        )
        .toBeVisible()
    })
})
