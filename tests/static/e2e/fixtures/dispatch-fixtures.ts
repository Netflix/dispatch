import { test as base } from "@playwright/test"
import { AuthPage } from "../pages/auth-page"
import { ReportIncidentPage } from "../pages/report-incident-page"
import { IncidentsPage } from "../pages/incidents-page"
import { CasesPage } from "../pages/cases-page"
import { ReportCasePage } from "../pages/report-case-page"

type DispatchFixtures = {
  authPage: AuthPage
  reportIncidentPage: ReportIncidentPage
  incidentsPage: IncidentsPage
  casesPage: CasesPage
  reportCasePage: ReportCasePage
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

  reportCasePage: async ({ page }, use) => {
    await use(new ReportCasePage(page))
  },

})
export { expect } from "@playwright/test"
