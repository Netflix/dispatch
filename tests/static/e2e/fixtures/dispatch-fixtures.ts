import { test as base } from "@playwright/test"
import { AuthPage } from "../pages/auth-page"
import { ReportIncidentPage } from "../pages/report-incident-page"
import { IncidentsPage } from "../pages/incidents-page"

type DispatchFixtures = {
  authPage: AuthPage
  reportIncidentPage: ReportIncidentPage
  incidentsPage: IncidentsPage
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
})
export { expect } from "@playwright/test"
