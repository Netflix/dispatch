import { mount } from "@vue/test-utils"
import { expect, test } from "vitest"
import { createVuetify } from "vuetify"
import * as components from "vuetify/components"
import * as directives from "vuetify/directives"
import LockButton from "@/components/LockButton.vue"

const vuetify = createVuetify({
  components,
  directives,
})

global.ResizeObserver = require("resize-observer-polyfill")

test("mounts correctly", () => {
  const wrapper = mount(LockButton, {
    props: {
      subjectVisibility: "Open",
      subjectType: "incident",
    },
    global: {
      plugins: [vuetify],
    },
  })

  expect(wrapper.exists()).toBe(true)
})

test("opens dialog on button click", async () => {
  const wrapper = mount(LockButton, {
    props: {
      subjectVisibility: "Open",
      subjectType: "incident",
    },
    global: {
      plugins: [vuetify],
    },
  })

  // find the button and trigger click event
  await wrapper.find("button").trigger("click")

  // assert that dialog is visible
  expect(wrapper.findComponent({ name: "v-dialog" }).isVisible()).toBe(true)
})
