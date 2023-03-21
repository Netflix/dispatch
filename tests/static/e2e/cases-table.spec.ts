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
      await casesPage.RowActionKebab.click()
      await expect.soft(casesPage.ViewEditMenuItem).toBeVisible()
      await expect.soft(casesPage.DeleteMenuItem).toBeVisible()
    }),
    test("The case edit pane should be visible.", async ({
      casesPage, casesViewEditModal
    }) => {
      await casesPage.goto()
      await casesPage.RowActionKebab.click()
      await casesPage.ViewEditMenuItem.click()
      await expect(casesViewEditModal.EscalateButton).toBeVisible()
    })
    test("The case escalate modal should be visible.", async ({
      casesPage, casesViewEditModal, caseEscalateModal
    }) => {
      await casesPage.goto()
      await casesPage.RowActionKebab.click()
      await casesPage.ViewEditMenuItem.click()
      await casesViewEditModal.EscalateButton.click()
      await expect(caseEscalateModal.SubmitButton).toBeVisible()
    })
    test("The case escalate submission modal should be visible.", async ({
      casesPage, casesViewEditModal, caseEscalateModal, caseEscalateSubmissionModal
    }) => {
      await casesPage.goto()
      await casesPage.RowActionKebab.click()
      await casesPage.ViewEditMenuItem.click()
      await casesViewEditModal.EscalateButton.click()
      await caseEscalateModal.SubmitButton.click()
      await expect(caseEscalateSubmissionModal.SubmitButton).toBeVisible()
    })
})
