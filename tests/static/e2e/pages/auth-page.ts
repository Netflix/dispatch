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
    console.log(`Successfully navigated to register page: ${this.page.url()}`)
  }

  /**
   * Wait for the application to be fully ready by checking that all necessary elements are loaded
   * and the page is stable. This replaces the previous 2-minute static wait.
   */
  async waitForAppReady() {
    // First, wait for the server to be responsive
    const maxAttempts = 10
    let attempt = 0

    while (attempt < maxAttempts) {
      try {
        const response = await this.page.request.get("/api/v1/auth/me", {
          failOnStatusCode: false,
        })

        // If we get any response (even 401), the server is ready
        if (response.status() === 401 || response.status() === 200) {
          console.log("Server is responsive")
          break
        }
      } catch (error) {
        console.log(`Server not ready yet (attempt ${attempt + 1}/${maxAttempts})`)
      }

      attempt++
      if (attempt < maxAttempts) {
        await this.page.waitForTimeout(3000)
      }
    }

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

    // Add retry logic and better error handling
    const maxRetries = 3
    let retryCount = 0

    while (retryCount < maxRetries) {
      try {
        // Click register button
        await this.registerButton.click()

        // Wait for either dashboard or error state
        await Promise.race([
          this.page.waitForURL(orgSlug + Routes.Dashboards, {
            timeout: 30000,
            waitUntil: "networkidle",
          }),
          this.page.waitForURL(this.loginRoute, { timeout: 5000 }),
          this.page.waitForSelector(".v-alert", { timeout: 5000 }), // Wait for error alert
        ])

        // Check if we successfully navigated to dashboard
        if (this.page.url().includes(Routes.Dashboards)) {
          return // Success!
        }

        // Check if there's an error message
        const errorAlert = await this.page.locator(".v-alert").count()
        if (errorAlert > 0) {
          const errorText = await this.page.locator(".v-alert").textContent()
          throw new Error(`Registration failed: ${errorText}`)
        }

        // If we're on login page, try to login with the same credentials
        if (this.page.url().includes(Routes.Login)) {
          console.log("Registration redirected to login, attempting to login...")
          await this.emailLabel.fill(email)
          await this.passwordLabel.fill(password)
          await this.page.getByRole("button", { name: "Login" }).click()
          await this.page.waitForURL(orgSlug + Routes.Dashboards, {
            timeout: 30000,
            waitUntil: "networkidle",
          })
          return // Success via login!
        }

        retryCount++
        if (retryCount < maxRetries) {
          console.log(`Registration attempt ${retryCount} failed, retrying...`)
          await this.page.waitForTimeout(2000) // Wait before retry
        }
      } catch (error) {
        retryCount++
        if (retryCount >= maxRetries) {
          throw new Error(`Registration failed after ${maxRetries} attempts: ${error}`)
        }
        console.log(`Registration attempt ${retryCount} failed with error: ${error}, retrying...`)
        await this.page.waitForTimeout(2000) // Wait before retry
      }
    }

    throw new Error("Registration failed after all retry attempts")
  }

  async pageObjectModel(email: string, password: string) {
    await this.registerNewUser(email, password)
  }
}
