import { expect, Locator, Page } from "@playwright/test"
import { orgSlug, Routes } from "../routes"

export class ReportIncidentPage {
  readonly page: Page
  readonly route: string
  readonly reportHeader: Locator
  readonly titleTextBox: Locator
  readonly descriptionTextBox: Locator
  readonly projectDropdown: Locator
  readonly typeDropdown: Locator
  readonly priorityDropdown: Locator
  readonly tagsDropdown: Locator
  readonly submitButton: Locator
  readonly loadMore: Locator
  readonly pageBorder: Locator

  constructor(page: Page) {
    this.page = page
    this.route = orgSlug + Routes.ReportIncident
    this.reportHeader = page.getByText("Report Incident").first()
    this.titleTextBox = page.getByLabel("Title", { exact: true })
    this.descriptionTextBox = page.getByLabel("Description", { exact: true })
    this.projectDropdown = page.getByRole("combobox").filter({ hasText: "Project" })
    this.typeDropdown = page.getByRole("combobox").filter({ hasText: "Type" })
    this.priorityDropdown = page.getByRole("combobox").filter({ hasText: "Priority" })
    this.tagsDropdown = page.getByLabel("Tags", { exact: true })
    this.submitButton = page.getByRole("button", { name: "Submit" })
    this.loadMore = page.getByText("Load More")
    this.pageBorder = this.page.locator("span").filter({
      hasText: "Report Incident If you suspect an incident and need help",
    })
  }

  async goto() {
    await Promise.all([
      this.page.goto(this.route),
      await this.page.waitForURL(this.route),
      await expect(this.reportHeader).toBeVisible(),
    ])
  }

  async reportIncident(
    title: string,
    description: string,
    project: string = "default",
    type: string = "Customer Data",
    priority: string = "Low",
    tags: string[]
  ) {
    await this.goto()
    // give time for default project to settle
    await this.page.waitForTimeout(3000);
    await this.addTitle(title)
    await this.addDescription(description)
    await this.selectProject(project)
    await this.selectType(type)
    await this.selectPriority(priority)
    await this.selectTags(tags)
    // click outside tag select to update URL
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

  async selectTags(tags: string[]) {
    await this.tagsDropdown.click()
    for (const tag of tags) {
      if (!(await this.page.getByText("No tags matching").isVisible())) {
        await this.page.getByRole('checkbox', { name: tag }).check()
      }
    }
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
    await this.reportIncident(title, description, project, type, priority, tags)
  }
}
