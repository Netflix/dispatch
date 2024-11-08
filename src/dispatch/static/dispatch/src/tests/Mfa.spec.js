import { mount, flushPromises } from "@vue/test-utils"
import { expect, test, vi, beforeEach, afterEach } from "vitest"
import { createVuetify } from "vuetify"
import * as components from "vuetify/components"
import * as directives from "vuetify/directives"
import MfaVerification from "@/auth/mfa.vue"
import authApi from "@/auth/api"

vi.mock("vue-router", () => ({
  useRoute: () => ({
    query: {
      challenge_id: "test-challenge",
      project_id: "123",
      action: "test-action",
    },
  }),
}))

vi.mock("@/auth/api", () => ({
  default: {
    verifyMfa: vi.fn(),
  },
}))

const vuetify = createVuetify({
  components,
  directives,
})

global.ResizeObserver = require("resize-observer-polyfill")

const windowCloseMock = vi.fn()
const originalClose = window.close

beforeEach(() => {
  vi.useFakeTimers()
  Object.defineProperty(window, "close", {
    value: windowCloseMock,
    writable: true,
  })
  vi.clearAllMocks()
})

afterEach(() => {
  vi.useRealTimers()
  Object.defineProperty(window, "close", {
    value: originalClose,
    writable: true,
  })
})

test("mounts correctly and starts verification automatically", async () => {
  const wrapper = mount(MfaVerification, {
    global: {
      plugins: [vuetify],
    },
  })

  await flushPromises()

  expect(wrapper.exists()).toBe(true)
  expect(authApi.verifyMfa).toHaveBeenCalledWith({
    challenge_id: "test-challenge",
    project_id: 123,
    action: "test-action",
  })
})

test("shows loading state while verifying", async () => {
  vi.mocked(authApi.verifyMfa).mockImplementationOnce(
    () => new Promise(() => {}) // Never resolving promise
  )

  const wrapper = mount(MfaVerification, {
    global: {
      plugins: [vuetify],
    },
  })

  await flushPromises()

  const loadingSpinner = wrapper.findComponent({ name: "v-progress-circular" })
  expect(loadingSpinner.exists()).toBe(true)
  expect(loadingSpinner.isVisible()).toBe(true)
})

test("shows success message and closes window on approval", async () => {
  vi.mocked(authApi.verifyMfa).mockResolvedValueOnce({
    data: { status: "approved" },
  })

  const wrapper = mount(MfaVerification, {
    global: {
      plugins: [vuetify],
    },
  })

  await flushPromises()

  const alert = wrapper.findComponent({ name: "v-alert" })
  expect(alert.exists()).toBe(true)
  expect(alert.props("type")).toBe("success")
  expect(alert.text()).toContain("MFA verification successful")

  vi.advanceTimersByTime(5000)
  expect(windowCloseMock).toHaveBeenCalled()
})

test("shows error message and retry button on denial", async () => {
  vi.mocked(authApi.verifyMfa).mockResolvedValueOnce({
    data: { status: "denied" },
  })

  const wrapper = mount(MfaVerification, {
    global: {
      plugins: [vuetify],
    },
  })

  await flushPromises()

  const alert = wrapper.findComponent({ name: "v-alert" })
  expect(alert.exists()).toBe(true)
  expect(alert.props("type")).toBe("error")
  expect(alert.text()).toContain("MFA verification denied")

  const retryButton = wrapper.findComponent({ name: "v-btn" })
  expect(retryButton.exists()).toBe(true)
  expect(retryButton.text()).toContain("Retry Verification")
})

test("retry button triggers new verification attempt", async () => {
  const verifyMfaMock = vi
    .mocked(authApi.verifyMfa)
    .mockResolvedValueOnce({
      data: { status: "denied" },
    })
    .mockResolvedValueOnce({
      data: { status: "approved" },
    })

  const wrapper = mount(MfaVerification, {
    global: {
      plugins: [vuetify],
    },
  })

  await flushPromises()

  const retryButton = wrapper.findComponent({ name: "v-btn" })
  await retryButton.trigger("click")

  await flushPromises()

  expect(verifyMfaMock).toHaveBeenCalledTimes(2)

  const alert = wrapper.findComponent({ name: "v-alert" })
  expect(alert.props("type")).toBe("success")
})

test("handles API errors gracefully", async () => {
  vi.mocked(authApi.verifyMfa).mockRejectedValueOnce(new Error("API Error"))

  const wrapper = mount(MfaVerification, {
    global: {
      plugins: [vuetify],
    },
  })

  await flushPromises()

  const alert = wrapper.findComponent({ name: "v-alert" })
  expect(alert.exists()).toBe(true)
  expect(alert.props("type")).toBe("error")
  expect(alert.text()).toContain("MFA verification denied")
})
