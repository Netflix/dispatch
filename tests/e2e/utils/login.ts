import { Page } from "@playwright/test"

async function login(page: Page): Promise<void> {
  let email = (Math.random() + 1).toString(36).substring(7) + "@example.com"
  let password = (Math.random() + 1).toString(36).substring(7)

  // Wait for 30 seconds to be sure web server is fully init
  await page.waitForTimeout(30000)

  // baseURL is set in the config to http://localhost:8080/
  // This will navigate to http://localhost:8080/default/auth/login
  await page.goto("./default/auth/login")

  await page.getByRole("link", { name: "Register" }).click()

  await page.getByLabel("Email").click()
  await page.getByLabel("Email").fill(email)

  await page.getByLabel("Password").click()
  await page.getByLabel("Password").fill(password)
  await page.getByRole("button", { name: "Register" }).click()
  // Browse to Dashboards page to make sure we logged in
  await page.getByRole("listitem").filter({ hasText: "Dashboards" }).click()
}

export default login
