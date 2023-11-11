import { expect, Locator, Page } from "@playwright/test"
import { Routes, orgSlug } from "../routes"

export class IncidentsPage {
  readonly page: Page
  readonly route: string
  readonly Row: Locator
  readonly FirstRow: Locator
  readonly OtherRow: Locator
  readonly NextPage: Locator
  readonly EditKebab: Locator
  readonly EditMenu: Locator
  readonly EditViewEdit: Locator
  readonly EditCreateReport: Locator
  readonly EditRunWorkflow: Locator
  readonly EditDelete: Locator

  constructor(page: Page, incident: string = `dispatch-${orgSlug}-${orgSlug}-2`) {
    this.page = page
    this.route = orgSlug + Routes.Incidents
    this.Row = page.locator("tr")
    this.NextPage = page.getByRole("button", { name: "Next page" })
    this.EditKebab = page
      .getByRole("row", {
        name: incident,
      })
      .getByRole("button")
      .nth(2)
    this.EditMenu = page.getByTestId("incident-table-edit")
    this.EditViewEdit = page.getByText("View / Edit", { exact: true })
    this.EditCreateReport = page.getByText("Create Report", { exact: true })
    this.EditRunWorkflow = page.getByText("Run Workflow", { exact: true })
    this.EditDelete = page.getByText("Delete", { exact: true })
  }

  async goto() {
    await Promise.all([this.page.goto(this.route), await this.page.waitForURL(this.route)])
  }
}
