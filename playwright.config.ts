import type { PlaywrightTestConfig } from "@playwright/test"
import { devices } from "@playwright/test"

/**
 * @see https://playwright.dev/docs/test-configuration
 */
const config: PlaywrightTestConfig = {
  testDir: "./tests/static/e2e",
  outputDir: "./tests/static/e2e/artifacts/test-failures",
  use: {
    /* Maximum time each action such as `click()` can take. Defaults to 0 (no limit). */
    actionTimeout: 0,
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: "http://localhost:8080/",
    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: "retain-on-failure",
    video: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  /* Maximum time one test can run for. */
  timeout: process.env.CI ? 200 * 1000 : 60 * 1000,
  expect: {
    /**
     * Maximum time expect() should wait for the condition to be met.
     * For example in `await expect(locator).toHaveText();`
     */
    timeout: process.env.CI ? 20000 : 10000,
  },
  /* Run tests in files in parallel */
  fullyParallel: true,
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,
  /* Optimize workers for CI - use more workers for faster execution */
  workers: process.env.CI ? 4 : undefined,
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: process.env.CI ? [["html"], ["github"]] : "html",
  /* Configure projects for major browsers */
  projects: process.env.CI
    ? [
        {
          name: "chromium",
          use: {
            ...devices["Desktop Chrome"],
          },
        },
      ]
    : [
        {
          name: "chromium",
          use: {
            ...devices["Desktop Chrome"],
          },
        },
        {
          name: "firefox",
          use: {
            ...devices["Desktop Firefox"],
          },
        },
        {
          name: "webkit",
          use: {
            ...devices["Desktop Safari"],
          },
        },
      ],
  /* Folder for test artifacts such as screenshots, videos, traces, etc. */
  // outputDir: 'test-results/',

  /* Run your local dev server before starting the tests */
  webServer: {
    command: "dispatch server develop",
    url: "http://localhost:8080/",
    reuseExistingServer: !process.env.CI,
    /* Increase timeout to allow server to fully start and settle - especially important after removing the 2-minute wait from tests */
    timeout: 240 * 1000, // 4 minutes to ensure server is fully ready
  },
}

export default config
