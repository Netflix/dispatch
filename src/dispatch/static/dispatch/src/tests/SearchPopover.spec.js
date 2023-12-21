import { mount } from "@vue/test-utils"
import { expect, test } from "vitest"
import { createVuetify } from "vuetify"
import * as components from "vuetify/components"
import * as directives from "vuetify/directives"
import Hotkey from "@/atomics/Hotkey.vue"
import SearchPopover from "@/components/SearchPopover.vue"

const vuetify = createVuetify({
  components,
  directives,
})

global.ResizeObserver = require("resize-observer-polyfill")

test("mounts correctly", () => {
  const wrapper = mount(SearchPopover, {
    props: {
      hotkeys: ["a", "b", "c"],
      initialValue: "Initial",
      items: ["Item 1", "Item 2", "Item 3"],
      label: "Label",
    },
    global: {
      plugins: [vuetify],
      components: {
        Hotkey,
      },
    },
  })

  expect(wrapper.exists()).toBe(true)
})

test("toggles menu on button click", async () => {
  const wrapper = mount(SearchPopover, {
    props: {
      hotkeys: ["a", "b", "c"],
      initialValue: "Initial",
      items: ["Item 1", "Item 2", "Item 3"],
      label: "Label",
    },
    global: {
      plugins: [vuetify],
      components: {
        Hotkey,
      },
    },
  })

  // assert that menu is not visible initially
  expect(wrapper.vm.menu).toBe(false)

  // find the button and trigger click event
  await wrapper.find(".menu-activator").trigger("click")

  // assert that menu is visible after click
  expect(wrapper.vm.menu).toBe(true)
})

test("updates selectedItem when selectItem is called", async () => {
  const wrapper = mount(SearchPopover, {
    props: {
      hotkeys: ["a", "b", "c"],
      initialValue: "Initial",
      items: ["Item 1", "Item 2", "Item 3"],
      label: "Label",
    },
    global: {
      plugins: [vuetify],
      components: {
        Hotkey,
      },
    },
  })

  // assert that selectedItem is initialValue initially
  expect(wrapper.vm.selectedItem).toBe("Initial")

  // call selectItem method
  await wrapper.vm.selectItem("Item 2")

  // assert that selectedItem is updated
  expect(wrapper.vm.selectedItem).toBe("Item 2")
})

test("updates searchQuery when text field input changes", async () => {
  const wrapper = mount(SearchPopover, {
    props: {
      hotkeys: ["a", "b", "c"],
      initialValue: "Initial",
      items: ["Item 1", "Item 2", "Item 3"],
      label: "Label",
    },
    global: {
      plugins: [vuetify],
      components: {
        Hotkey,
      },
    },
  })

  // find the button and trigger click event
  await wrapper.find(".menu-activator").trigger("click")

  // assert that searchQuery is empty initially
  expect(wrapper.vm.searchQuery).toBe("")

  // find the text field and trigger input event
  await wrapper.findComponent({ name: "v-text-field" }).setValue("Item 2")

  // assert that searchQuery is updated
  expect(wrapper.vm.searchQuery).toBe("Item 2")
})

test("filters items based on searchQuery", async () => {
  const wrapper = mount(SearchPopover, {
    props: {
      hotkeys: ["a", "b", "c"],
      initialValue: "Initial",
      items: ["Apple", "Banana", "Cherry"],
      label: "Label",
    },
    global: {
      plugins: [vuetify],
      components: {
        Hotkey,
      },
    },
  })

  // find the button and trigger click event
  await wrapper.find(".menu-activator").trigger("click")

  // assert that all items are present initially
  expect(wrapper.vm.filteredItems).toEqual(["Apple", "Banana", "Cherry"])

  // simulate user input in the text field
  await wrapper.findComponent({ name: "v-text-field" }).setValue("an")

  // assert that items are filtered based on searchQuery
  expect(wrapper.vm.filteredItems).toEqual(["Banana"])
})

test("emits item-selected when an item is selected", async () => {
  const wrapper = mount(SearchPopover, {
    props: {
      hotkeys: ["a", "b", "c"],
      initialValue: "Initial",
      items: ["Apple", "Banana", "Cherry"],
      label: "Label",
    },
    global: {
      plugins: [vuetify],
      components: {
        Hotkey,
      },
    },
  })

  // call selectItem method
  await wrapper.vm.selectItem("Banana")

  // assert that 'item-selected' event is emitted with the correct item
  expect(wrapper.emitted()).toHaveProperty("item-selected")
  expect(wrapper.emitted()["item-selected"]).toEqual([["Banana"]])
})

test("updates selectedItem when initialValue prop changes", async () => {
  const wrapper = mount(SearchPopover, {
    props: {
      hotkeys: ["a", "b", "c"],
      initialValue: "Initial",
      items: ["Apple", "Banana", "Cherry"],
      label: "Label",
    },
    global: {
      plugins: [vuetify],
      components: {
        Hotkey,
      },
    },
  })

  // change initialValue prop
  await wrapper.setProps({ initialValue: "New Value" })

  // assert that selectedItem is updated
  expect(wrapper.vm.selectedItem).toBe("New Value")
})

test("updates items when items prop changes", async () => {
  const wrapper = mount(SearchPopover, {
    props: {
      hotkeys: ["a", "b", "c"],
      initialValue: "Initial",
      items: ["Apple", "Banana", "Cherry"],
      label: "Label",
    },
    global: {
      plugins: [vuetify],
      components: {
        Hotkey,
      },
    },
  })

  // change items prop
  await wrapper.setProps({ items: ["Item 1", "Item 2", "Item 3"] })

  // assert that items is updated
  expect(wrapper.vm.items).toEqual(["Item 1", "Item 2", "Item 3"])
})
