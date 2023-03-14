import { expect, Locator, Page } from "@playwright/test"
import { orgSlug, Routes } from "../routes"

export class ReportCasePage {
  readonly page: Page
  readonly route: string
  readonly reportHeader: Locator
  readonly titleTextBox: Locator
  readonly descriptionTextBox: Locator
  readonly projectDropdown: Locator
  readonly submitButton: Locator
  readonly pageBorder: Locator

  constructor(page: Page) {
    this.page = page
    this.route = orgSlug + Routes.ReportCase
    this.reportHeader = page.getByText("Report Case").first()
    this.titleTextBox = page.getByLabel("Title")
    this.descriptionTextBox = page.getByLabel("Description")
    this.projectDropdown = page.getByRole("combobox").filter({ hasText: "Project" }).locator("i")
    this.submitButton = page.getByRole("button", { name: "Submit" })
    this.pageBorder = this.page.locator("span").filter({
      hasText: "Report Case If you suspect an incident and need help",
    })
  }

  async goto() {
    await Promise.all([
      this.page.goto(this.route),
      await this.page.waitForURL(this.route),
      await expect(this.reportHeader).toBeVisible(),
    ])
  }

  async reportCase(
    title: string,
    description: string,
    project: string = "default",
  ) {
    await this.goto()
    await this.addTitle(title)
    await this.addDescription(description)
    await this.selectProject(project)
    await this.resetPageView()
    await Promise.all([
      await this.submitButton.click(),
      await this.page.waitForLoadState("networkidle"),
    ])
  }

  async addTitle(title: string) {
    await this.titleTextBox.click()
    await this.titleTextBox.fill(title)
  }

  async addDescription(description: string) {
    await this.descriptionTextBox.click()
    await this.descriptionTextBox.fill(description)
  }

  async selectProject(project: string) {
    await this.projectDropdown.click()
    await this.page.getByText(project, { exact: true }).click()
  }


  async resetPageView() {
    await this.pageBorder.click()
  }

  async pageObjectModel(
    title: string,
    description: string,
    project: string = "default",
  ) {
    await this.reportCase(title, description, project)
  }
}
