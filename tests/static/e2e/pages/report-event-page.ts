import { expect, Locator, Page } from "@playwright/test"
import { orgSlug, Routes } from "../routes"

export class ReportEventPage {
  readonly page: Page
  readonly route: string
  readonly reportHeader: Locator
  readonly descriptionTextBox: Locator
  readonly urgentCheckbox: Locator
  readonly submitButton: Locator
  readonly pageBorder: Locator

  constructor(page: Page) {
    this.page = page
    this.route = orgSlug + Routes.ReportEvent
    this.reportHeader = page.getByText("Report a Security Event").first()
    this.descriptionTextBox = page.getByLabel("Description", { exact: true })
    this.urgentCheckbox = page.getByLabel(
      "URGENT: I need immediate help with this (the oncall will be paged)",
      { exact: true }
    )
    this.submitButton = page.getByRole("button", { name: "Submit" })
    this.pageBorder = this.page.locator("span").filter({
      hasText: "Security Events are an input",
    })
  }

  async goto() {
    await Promise.all([
      this.page.goto(this.route),
      await this.page.waitForURL(this.route),
      await expect(this.reportHeader).toBeVisible(),
    ])
  }

  async reportEvent(description: string, urgent: boolean = false) {
    await this.goto()
    // give time for default project to settle
    await this.page.waitForTimeout(3000)
    await this.addDescription(description)
    if (urgent) {
      await this.urgentCheckbox.click()
    }
    await this.page.waitForTimeout(1500)
    await this.resetPageView()
    await Promise.all([
      await this.submitButton.click(),
      await this.page.waitForLoadState("networkidle"),
    ])
  }

  async addDescription(description: string) {
    await this.descriptionTextBox.click()
    await this.descriptionTextBox.fill(description)
  }

  async resetPageView() {
    // await this.pageBorder.click()
  }

  async pageObjectModel(description: string, urgent: boolean = false) {
    await this.reportEvent(description, urgent)
  }
}
