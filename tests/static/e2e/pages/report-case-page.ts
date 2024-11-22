import { expect, Locator, Page } from "@playwright/test"
import { orgSlug, Routes } from "../routes"

export class ReportCasePage {
  readonly page: Page
  readonly route: string
  readonly reportHeader: Locator
  readonly titleTextBox: Locator
  readonly descriptionTextBox: Locator
  readonly projectDropdown: Locator
  readonly typeDropdown: Locator
  readonly priorityDropdown: Locator
  readonly submitButton: Locator
  readonly pageBorder: Locator

  constructor(page: Page) {
    this.page = page
    this.route = orgSlug + Routes.ReportCase
    this.reportHeader = page.getByText("Open a Case").first()
    this.titleTextBox = page.getByLabel("Title", { exact: true })
    this.descriptionTextBox = page.getByLabel("Description", { exact: true })
    this.projectDropdown = page.getByRole("combobox").filter({ hasText: "Project" })
    this.typeDropdown = page.getByRole("combobox").filter({ hasText: "Type" })
    this.priorityDropdown = page.getByRole("combobox").filter({ hasText: "Priority" })
    this.submitButton = page.getByRole("button", { name: "Submit" })
    this.pageBorder = this.page.locator("span").filter({
      hasText: "Cases are meant to triage events",
    })
  }

  async goto() {
    await Promise.all([
      this.page.goto(this.route),
      this.page.waitForURL(this.route),
    ]);

    await expect(this.reportHeader).toBeVisible();
  }


  async reportCase(
    title: string,
    description: string,
    project: string = "default",
    type: string = "Security Triage",
    priority: string = "Low",
  ) {
    await this.goto()
    // give time for default project to settle
    await this.page.waitForTimeout(3000);
    await this.addTitle(title)
    await this.addDescription(description)
    await this.selectProject(project)
    await this.selectType(type)
    await this.selectPriority(priority)
    await this.page.waitForTimeout(1500);
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
    await this.page.getByText(project, { exact: true }).first().click()
  }

  async selectType(type: string) {
    await this.typeDropdown.click()
    await this.page.getByText(type, { exact: true }).click()
  }

  async selectPriority(priority: string) {
    await this.priorityDropdown.click()
    await this.page.getByText(priority, { exact: true }).click()
  }

  async resetPageView() {
    // await this.pageBorder.click()
  }

  async pageObjectModel(
    title: string,
    description: string,
    project: string = "default",
    type: string,
    priority: string = "Low",
    tags: string[]
  ) {
    await this.reportCase(title, description, project, type, priority, tags)
  }
}
