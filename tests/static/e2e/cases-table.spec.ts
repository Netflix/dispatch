import { test as base, expect } from '@playwright/test';
import { myAccount, DispatchUserFixtures } from './fixtures/user-fixtures';
import { myPage, DispatchPageFixtures } from './fixtures/page-fixtures';

const test = base.extend<DispatchUserFixtures & DispatchPageFixtures>({ ...myAccount, ...myPage });

test.describe("CaseTable", () => {
  test("The edit list should appear after clicking the case edit kebab.", async ({
    adminAccount, casesPage,
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
  test("The case escalate submission receipt should be visable.", async ({
    casesPage, casesViewEditModal, caseEscalateModal, caseEscalateSubmissionModal
  }) => {
    await casesPage.goto()
    await casesPage.RowActionKebab.click()
    await casesPage.ViewEditMenuItem.click()
    await casesViewEditModal.EscalateButton.click()
    await caseEscalateModal.SubmitButton.click()
    await caseEscalateSubmissionModal.SubmitButton.click()
    await expect(caseEscalateSubmissionModal.IncidentTitle).toBeVisible()
  })
})
