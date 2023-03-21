import { test as base } from "@playwright/test"
import { AuthPage } from "../pages/auth-page"
import { ReportIncidentPage } from "../pages/report-incident-page"
import { IncidentsPage } from "../pages/incidents-page"
import { CaseEscalateModal, CaseEscalateSubmissionModal, CasesPage, CasesViewEditModal } from "../pages/cases-page"
import { ReportCasePage } from "../pages/report-case-page"

type DispatchFixtures = {
  authPage: AuthPage
  reportIncidentPage: ReportIncidentPage
  incidentsPage: IncidentsPage
  casesPage: CasesPage
  reportCasePage: ReportCasePage
  casesViewEditModal: CasesViewEditModal
  caseEscalateModal: CaseEscalateModal
  caseEscalateSubmissionModal: CaseEscalateSubmissionModal
}

export const test = base.extend<DispatchFixtures>({
  authPage: async ({ page }, use) => {
    await use(new AuthPage(page))
  },

  reportIncidentPage: async ({ page }, use) => {
    await use(new ReportIncidentPage(page))
  },

  incidentsPage: async ({ page }, use) => {
    const incidentsPage = new IncidentsPage(page)
    await use(incidentsPage)
  },

  casesPage: async ({page}, use) => {
    const casesPage = new CasesPage(page)
    await use(casesPage)
  },

  casesViewEditModal: async ({page}, use) => {
    const casesViewEditModal = new CasesViewEditModal(page)
    await use(casesViewEditModal)
  },

  caseEscalateModal: async ({page}, use) => {
    const caseEscalateModal = new CaseEscalateModal(page)
    await use(caseEscalateModal)
  },

  caseEscalateSubmissionModal:async ({ page }, use) => {
    const caseEscalateSubmissionModal = new CaseEscalateSubmissionModal(page)
    await use(caseEscalateSubmissionModal)
  },

  reportCasePage: async ({ page }, use) => {
    await use(new ReportCasePage(page))
  },

})
export { expect } from "@playwright/test"
