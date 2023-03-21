import { expect, Locator, Page } from "@playwright/test"
import { Routes, orgSlug } from "../routes"



export class CaseEscalateSubmissionModal {
  readonly page: Page
  readonly SubmitButton: Locator
  readonly IncidentTitle: Locator

  constructor(page: Page) {
    this.SubmitButton = page.getByRole('button', { name: 'Escalate', exact: true })
    this.IncidentTitle = page.getByText('incident')
  }
}

export class CaseEscalateModal {
  readonly page: Page
  readonly SubmitButton: Locator

  constructor(page: Page) {
    this.SubmitButton = page.getByRole('button', { name: 'Escalate', exact: true })
  }
}

export class CasesViewEditModal {
  readonly page: Page
  readonly EscalateButton: Locator

  constructor(page: Page) {
    this.EscalateButton = page.getByRole('button', { name: 'Escalate Case' })
  }
}

export class CasesPage {
  readonly page: Page
  readonly route: string
  readonly RowActionKebab: Locator
  readonly ViewEditMenuItem: Locator
  readonly DeleteMenuItem: Locator

  constructor(page: Page) {
    this.page = page
    this.route = orgSlug + Routes.Cases
    this.RowActionKebab = page
      .locator('td:nth-child(12)').first()
      .getByRole("button")
    this.ViewEditMenuItem = page.getByRole("menuitem", { name: "View / Edit" })
    this.DeleteMenuItem = page.getByRole("menuitem", { name: "Delete" })
  }

  async goto() {
    await Promise.all([this.page.goto(this.route), await this.page.waitForURL(this.route)])
  }
}
