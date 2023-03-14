import { expect, Locator, Page } from "@playwright/test"
import { Routes, orgSlug } from "../routes"

export class CasesPage {
  readonly page: Page
  readonly route: string
  readonly Row: Locator
  readonly FirstRow: Locator
  readonly OtherRow: Locator
  readonly NextPage: Locator
  readonly EditKebab: Locator
  readonly EditMenu: Locator
  readonly EditViewEdit: Locator
  readonly EditDelete: Locator

  constructor(page: Page, caseManagement: string = `dispatch-${orgSlug}-${orgSlug}-2`) {
    this.page = page
    this.route = orgSlug + Routes.Cases
    this.Row = page.locator("tr")
    this.NextPage = page.getByRole("button", { name: "Next page" })
    this.EditKebab = page
      .getByRole("row", {
        name: caseManagement,
      })
      .getByRole("button")
      .nth(2)
    this.EditMenu = page.getByTestId("case-table-edit")
    this.EditViewEdit = page.getByRole("menuitem", { name: "View / Edit" })
    this.EditDelete = page.getByRole("menuitem", { name: "Delete" })
  }

  async goto() {
    await Promise.all([this.page.goto(this.route), await this.page.waitForURL(this.route)])
  }
}
