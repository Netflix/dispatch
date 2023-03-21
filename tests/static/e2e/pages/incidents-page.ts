import { expect, Locator, Page } from "@playwright/test"
import { Routes, orgSlug } from "../routes"

export class IncidentsPage {
  readonly page: Page
  readonly route: string
  readonly EditKebab: Locator
  readonly EditViewEdit: Locator
  readonly EditCreateReport: Locator
  readonly EditRunWorkflow: Locator
  readonly EditDelete: Locator

  constructor(page: Page, incident: string = `dispatch-${orgSlug}-${orgSlug}-2`) {
    this.page = page
    this.route = orgSlug + Routes.Incidents
    this.EditKebab = page
      .locator('td:nth-child(12)').first()
      .getByRole("button")
    this.EditViewEdit = page.getByRole("menuitem", { name: "View / Edit" })
    this.EditCreateReport = page.getByRole("menuitem", { name: "Create Report" })
    this.EditRunWorkflow = page.getByRole("menuitem", { name: "Run Workflow" })
    this.EditDelete = page.getByRole("menuitem", { name: "Delete" })
  }

  async goto() {
    await Promise.all([this.page.goto(this.route), await this.page.waitForURL(this.route)])
  }
}
