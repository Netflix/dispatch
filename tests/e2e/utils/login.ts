import { Page } from "@playwright/test"

async function login(page: Page): Promise<void> {
  const user = ""
  const password = ""
  // baseURL is set in the config to http://localhost:8080/
  // This will navigate to http://localhost:8080/default/auth/login
  await page.goto("./default/auth/login")
  await page.getByLabel("Email").click()
  await page.getByLabel("Email").fill(user)
  await page.getByLabel("Password").click()
  await page.getByLabel("Password").fill(password)
  await page.getByRole("button", { name: "Login" }).click()
  // Browse to Dashboards page to make sure we logged in
  await page.getByRole("listitem").filter({ hasText: "Dashboards" }).click()
}

export default login
