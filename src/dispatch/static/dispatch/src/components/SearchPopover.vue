<script setup lang="ts">
import { computed, ref, defineEmits, watch } from "vue"
import { useHotKey } from "@/composables/useHotkey"
import type { Ref } from "vue"

const props = defineProps<{
  hotkeys: Array<string>
  initialValue: string
  items: Array<any>
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
  console.log("Got select item")
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
      <template v-slot:activator="{ props: menu }">
        <v-btn
          class="menu-activator text-subtitle-2 font-weight-regular"
          variant="text"
          v-bind="menu"
          :ripple="false"
        >
          <span style="font-size: 0.8125rem; font-weight: 500; color: rgb(60, 65, 73)">
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
              <template v-slot:label>
                <span class="text-subtitle-2 font-weight-regular"> {{ props.label }} </span>
              </template>
            </v-text-field>
          </v-col>
          <v-col align-self="end" cols="2" class="pb-2">
            <template v-for="(hotkey, _) in props.hotkeys" :key="`hotkey-${index}`">
              <Hotkey :hotkey="hotkey.toUpperCase()" />
            </template>
          </v-col>
        </v-row>
        <v-divider></v-divider>
        <v-list lines="one">
          <template v-for="(item, _) in filteredItems" :key="index">
            <v-list-item
              @click="selectItem(item)"
              @mouseover="hoveredData = item"
              @mouseleave="hoveredData = ''"
              density="compact"
              rounded="lg"
              class="ml-1 mr-1"
              active-class="ma-4"
            >
              <span class="item-title-font">
                <slot :item="item" />
              </span>
            </v-list-item>
          </template>
        </v-list>
      </v-card>
    </v-menu>
  </div>
</template>

<style scoped>
.dispatch-side-card {
  backdrop-filter: blur(12px) saturate(190%) contrast(50%) brightness(130%) !important;
  border: 0.5px solid rgb(216, 216, 216) !important;
  border-radius: 8px !important;
  box-shadow: rgba(0, 0, 0, 0.09) 0px 3px 12px !important;
  color: rgb(60, 65, 73) !important;
  opacity: 2 !important;
}

.item-title-font {
  font-size: 13px !important;
}

.menu-activator {
  border: 1px solid transparent;
}

.menu-activator:hover {
  border: 1px solid rgb(239, 241, 244) !important;
  border-radius: 4px; /* adjust as needed */
}
</style>
