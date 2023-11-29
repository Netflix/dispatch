<script setup lang="ts">
import { computed, ref, watch } from "vue"
import { useHotKey } from "@/composables/useHotkey"
import type { Ref } from "vue"

const props = defineProps<{
  hotkeys: string[]
  initialValue: string
  items: any[]
  label: string
}>()

const emit = defineEmits(["item-selected"])

const menu: Ref<boolean> = ref(false)
const items: Ref<string[]> = ref(props.items)
const hoveredData: Ref<string> = ref("")
const selectedItem: Ref<string> = ref(props.initialValue)
const searchQuery: Ref<string> = ref("")

watch(
  () => props.initialValue,
  (newVal) => {
    selectedItem.value = newVal
  },
  { immediate: true }
)

watch(
  () => props.items,
  (newVal) => {
    items.value = newVal
  },
  { immediate: true }
)

useHotKey(props.hotkeys, () => {
  if (!menu.value) {
    toggleMenu()
  }
})

const selectItem = (item: any) => {
  selectedItem.value = item
  menu.value = false
  emit("item-selected", item)
}

const filteredItems = computed(() => {
  return items.value.filter((s) => s.toLowerCase().includes(searchQuery.value.toLowerCase()))
})

const toggleMenu = () => {
  menu.value = !menu.value
  if (!menu.value) {
    hoveredData.value = ""
  }
}
</script>

<template>
  <div>
    <v-menu
      v-model="menu"
      :close-on-content-click="false"
      location="start"
      offset="10"
      transition="false"
    >
      <template #activator="{ props: menuProps }">
        <v-btn
          class="menu-activator text-subtitle-2 font-weight-regular"
          variant="text"
          v-bind="menuProps"
          :ripple="false"
        >
          <span class="dispatch-text-subtitle">
            {{ selectedItem }}
          </span>
        </v-btn>
      </template>

      <v-card min-width="190" class="rounded-lg dispatch-side-card">
        <v-row no-gutters>
          <v-col align-self="start">
            <v-text-field
              v-model="searchQuery"
              density="compact"
              variant="solo"
              single-line
              hide-details
              flat
            >
              <template #label>
                <span class="text-subtitle-2 font-weight-regular"> {{ props.label }} </span>
              </template>
            </v-text-field>
          </v-col>
          <v-col align-self="end" cols="3" class="pb-2">
            <div v-for="(hotkey, index) in props.hotkeys" :key="`hotkey-${index}`">
              <Hotkey :hotkey="hotkey.toUpperCase()" />
            </div>
          </v-col>
        </v-row>
        <v-divider />
        <v-list lines="one">
          <div v-for="(item, index) in filteredItems" :key="`item-${index}`">
            <v-list-item
              @click="selectItem(item)"
              @mouseover="hoveredData = item"
              @mouseleave="hoveredData = ''"
              density="compact"
              rounded="lg"
              class="ml-1 mr-1"
              active-class="ma-4"
            >
              <span class="dispatch-text-title">
                <slot :item="item">{{ item }}</slot>
              </span>
            </v-list-item>
          </div>
        </v-list>
      </v-card>
    </v-menu>
  </div>
</template>

<style lang="scss" scoped>
@import "@/styles/index.scss";

.menu-activator {
  border: 1px solid transparent;
}

.menu-activator:hover {
  border: 1px solid rgb(239, 241, 244) !important;
  border-radius: 4px; /* adjust as needed */
}
</style>
