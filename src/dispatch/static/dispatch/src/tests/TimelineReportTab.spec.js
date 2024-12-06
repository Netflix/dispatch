import { mount, flushPromises } from "@vue/test-utils"
import { expect, test, vi, beforeEach } from "vitest"
import { createVuetify } from "vuetify"
import * as components from "vuetify/components"
import * as directives from "vuetify/directives"
import { createStore } from "vuex"
import { getField } from "vuex-map-fields"
import TimelineReportTab from "@/incident/TimelineReportTab.vue"

// Mock the filters
vi.mock("@/filters", () => ({
  formatToUTC: vi.fn((date) => date),
  formatToTimeZones: vi.fn((date) => date),
}))

const vuetify = createVuetify({
  components,
  directives,
})

global.ResizeObserver = require("resize-observer-polyfill")

// Mock data
const mockEvents = [
  {
    id: 1,
    started_at: "2023-01-01T10:00:00Z",
    source: "Incident Participant",
    description: "John Doe created a new tactical report",
    details: {
      conditions: "Current conditions",
      actions: "Planned actions",
      needs: "Resource needs",
    },
  },
  {
    id: 2,
    started_at: "2023-01-01T11:00:00Z",
    source: "Incident Participant",
    description: "Jane Smith created a new tactical report",
    details: {
      conditions: "Updated conditions",
      actions: "New actions",
      needs: "Additional needs",
    },
  },
  {
    id: 3,
    started_at: "2023-01-01T12:00:00Z",
    source: "Other Source",
    description: "This is not a tactical report",
    details: {},
  },
]

// Create a proper Vuex store mock
function createMockStore(events = mockEvents) {
  return createStore({
    modules: {
      incident: {
        namespaced: true,
        state: {
          selected: {
            events: events,
          },
        },
        getters: {
          getField, // This is required for vuex-map-fields to work
        },
      },
    },
  })
}

// Helper function to create wrapper
function createWrapper(events = mockEvents) {
  const store = createMockStore(events)
  return mount(TimelineReportTab, {
    global: {
      plugins: [vuetify, store],
    },
  })
}

beforeEach(() => {
  vi.clearAllMocks()
})

test("mounts correctly and displays tactical reports", async () => {
  const wrapper = createWrapper()
  await flushPromises()

  const timelineItems = wrapper.findAllComponents({ name: "v-timeline-item" })
  expect(timelineItems.length).toBe(3) // 2 tactical reports + 1 header item
})

test("filters out non-tactical report events", async () => {
  const wrapper = createWrapper()
  await flushPromises()

  const descriptions = wrapper.findAll(".v-col").map((col) => col.text())
  expect(descriptions.filter((d) => d.includes("tactical report")).length).toBe(2)
  expect(descriptions.filter((d) => d.includes("not a tactical report")).length).toBe(0)
})

test("displays event details correctly", async () => {
  const wrapper = createWrapper()
  await flushPromises()

  const cards = wrapper.findAllComponents({ name: "v-card" })
  const firstCard = cards[0]

  expect(firstCard.text()).toContain("Current conditions")
  expect(firstCard.text()).toContain("Planned actions")
  expect(firstCard.text()).toContain("Resource needs")
})

test("sorts events chronologically", async () => {
  const wrapper = createWrapper([...mockEvents].reverse())
  await flushPromises()

  const descriptions = wrapper.findAll(".v-col").map((col) => col.text())
  const tacticalReports = descriptions.filter((d) => d.includes("tactical report"))

  expect(tacticalReports[0]).toContain("John Doe")
  expect(tacticalReports[1]).toContain("Jane Smith")
})

test("displays UTC time notice", async () => {
  const wrapper = createWrapper()
  await flushPromises()

  const utcNotice = wrapper.find(".text-caption")
  expect(utcNotice.text()).toContain("UTC")
})

test("handles empty events array", async () => {
  const wrapper = createWrapper([])
  await flushPromises()

  const timelineItems = wrapper.findAllComponents({ name: "v-timeline-item" })
  expect(timelineItems.length).toBe(1) // Just the header item
})

test("displays correct icon for tactical reports", async () => {
  const wrapper = createWrapper()
  await flushPromises()

  const timelineItems = wrapper.findAllComponents({ name: "v-timeline-item" })
  // Subtract 1 for the header item which doesn't have an icon
  const itemsWithIcons = timelineItems.length - 1

  expect(itemsWithIcons).toBe(2) // Should have 2 tactical reports with icons

  const icons = wrapper.findAll(".v-icon")
  // Filter out any utility icons (like those in tooltips)
  const tacticalReportIcons = icons.filter((icon) => {
    const classes = icon.classes()
    return classes.includes("mdi-text-box-check")
  })

  expect(tacticalReportIcons.length).toBeGreaterThan(0)
})
