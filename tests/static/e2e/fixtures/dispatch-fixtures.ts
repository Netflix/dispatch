import { test as base } from "@playwright/test"
import { AuthPage } from "../pages/auth-page"
import { ReportIncidentPage } from "../pages/report-incident-page"
import { ReportCasePage } from "../pages/report-case-page"
import { IncidentsPage } from "../pages/incidents-page"
import { ReportEventPage } from "../pages/report-event-page"

type DispatchFixtures = {
  authPage: AuthPage
  reportIncidentPage: ReportIncidentPage
  reportCasePage: ReportCasePage
  incidentsPage: IncidentsPage
  reportEventPage: ReportEventPage
}

export const test = base.extend<DispatchFixtures>({
  authPage: async ({ page }, use) => {
    await use(new AuthPage(page))
  },

  reportIncidentPage: async ({ page }, use) => {
    await use(new ReportIncidentPage(page))
  },

  reportCasePage: async ({ page }, use) => {
    await use(new ReportCasePage(page))
  },

  reportEventPage: async ({ page }, use) => {
    await use(new ReportEventPage(page))
  },

  incidentsPage: async ({ page }, use) => {
    const incidentsPage = new IncidentsPage(page)
    await use(incidentsPage)
  },
})
export { expect } from "@playwright/test"
