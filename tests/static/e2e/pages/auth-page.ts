import { expect, Locator, Page } from "@playwright/test"
import { orgSlug, Routes } from "../routes"

export class AuthPage {
  readonly page: Page
  // Login
  readonly loginRoute: string
  readonly loginHeader: Locator
  // Register
  readonly registerRoute: string
  readonly registerHeader: Locator
  readonly registerLink: Locator
  readonly registerButton: Locator
  // Shared Components
  readonly emailLabel: Locator
  readonly passwordLabel: Locator

  constructor(page: Page) {
    this.page = page
    // Login
    this.loginRoute = orgSlug + Routes.Login
    this.loginHeader = page.getByText("Login").first()
    // Register
    this.registerRoute = orgSlug + Routes.Register
    this.registerHeader = page.getByText("Register").first()
    this.registerLink = page.getByRole("link", { name: "Register" })
    this.registerButton = page.getByRole("button", { name: "Register" })
    // Shared Components
    this.emailLabel = page.getByLabel("Email")
    this.passwordLabel = page.getByLabel("Password", { exact: true })
  }

  async gotoLogin() {
    await Promise.all([
      this.page.goto(this.loginRoute),
      await this.page.waitForURL(this.loginRoute),
      await expect(this.loginHeader).toBeVisible(),
    ])
  }

  async gotoRegisterWithLink() {
    await Promise.all([
      /*
        (wshel) Directly visiting register page will redirect the user to the login page.
        We must by click the register button on the login page.
      */
      await this.gotoLogin(),
      await this.registerLink.first().click(),
      await this.page.waitForURL(this.registerRoute),
      await expect(this.registerHeader).toBeVisible(),
    ])
  }

  /**
   * Wait for the application to be fully ready by checking that all necessary elements are loaded
   * and the page is stable. This replaces the previous 2-minute static wait.
   */
  async waitForAppReady() {
    // Wait for the page to be loaded and interactive
    await this.page.waitForLoadState("networkidle")

    // Additional wait to ensure any background initialization is complete
    // This is much shorter than the previous 2-minute wait but ensures stability
    await this.page.waitForTimeout(5000)

    // Verify the basic UI elements are working by ensuring we can navigate to login
    await this.page.goto(this.loginRoute, { waitUntil: "networkidle" })
    await expect(this.loginHeader).toBeVisible()
  }

  async registerNewUser(email: string, password: string) {
    // Ensure the application is ready before attempting registration
    await this.waitForAppReady()

    await this.gotoRegisterWithLink()
    await this.emailLabel.first().click()
    await this.emailLabel.fill(email)

    await this.passwordLabel.first().click()
    await this.passwordLabel.fill(password)

    await Promise.all([
      this.registerButton.click(),
      this.page.waitForURL(orgSlug + Routes.Dashboards),
    ])
  }

  async pageObjectModel(email: string, password: string) {
    await this.registerNewUser(email, password)
  }
}
