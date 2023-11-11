import { Locator, Page } from "@playwright/test"
import { Routes, orgSlug } from "../routes"

export class IncidentsPage {
  readonly page: Page
  readonly route: string

  readonly SaveButton: Locator
  readonly CloseButton: Locator

  readonly CostsTab: Locator
  readonly CostsAmount: Locator

  constructor(page: Page) {
    this.page = page
    this.route = orgSlug + Routes.Incidents

    this.SaveButton = page.getByRole("button").filter({ hasText: "save" })
    this.CloseButton = page.getByRole("button", { name: "Close" })

    this.CostsTab = page.getByRole("tab", { name: "Costs" })
    this.CostsAmount = page.getByLabel("Amount", { exact: true })
  }

  async goto(incident: string) {
    await Promise.all([
      this.page.goto(this.route + `/${incident}`),
      await this.page.waitForURL(this.route),
    ])
  }

  async addCost(incident: string) {
    await this.goto(incident)
    await this.CostsTab.first().click()
    await this.CostsAmount.click()
    await this.CostsAmount.fill("100000")
  }
}
