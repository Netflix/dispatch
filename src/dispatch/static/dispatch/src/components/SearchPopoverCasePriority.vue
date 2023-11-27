<script setup lang="ts">
import { ref, watch, defineEmits, computed, inject } from "vue"
import CasePriorityApi from "@/case/priority/api"
import { useHotKey } from "@/composables/useHotkey"
import type { Ref } from "vue"

type Priority = {
  name: string
  icon: string
  color: string
}

const props = defineProps<{ priority: string }>()

const menu: Ref<boolean> = ref(false)
const priorities: Ref<Priority[]> = ref([])
const hoveredPriority: Ref<string> = ref("")
const selectedPriority: Ref<Priority | null> = computed(() => {
  return (
    priorities.value.find((p) => p.name === props.priority) || {
      name: "Select Priority",
      icon: "mdi-help-circle", // Default icon
      color: "grey", // Default color
    }
  )
})
const searchQuery: Ref<string> = ref("")
const isMenuOpen: Ref<boolean> = inject("isMenuOpen")

useHotKey(["p"], () => {
  if (!menu.value) {
    toggleMenu()
  }
})

// Fetch priorities
const fetchPriorities = async () => {
  try {
    const response = await CasePriorityApi.getAll()
    const order = ["Critical", "High", "Medium", "Low"]
    priorities.value = response.data.items
      .map((item: any) => ({
        name: item.name,
        ...getPriorityIconAndColor(item.name),
      }))
      .sort((a, b) => order.indexOf(a.name) - order.indexOf(b.name))
  } catch (error) {
    console.error("Error fetching priorities:", error)
  }
}

const getPriorityIconAndColor = (name: string) => {
  switch (name) {
    case "Critical":
      return { icon: "mdi-alert-box", color: "black" }
    case "High":
      return { icon: "mdi-signal-cellular-3", color: "black" }
    case "Medium":
      return { icon: "mdi-signal-cellular-2", color: "black" }
    case "Low":
      return { icon: "mdi-signal-cellular-1", color: "black" }
    default:
      return { icon: "mdi-help-circle", color: "black" }
  }
}

const emit = defineEmits(["priority-selected"])

watch(
  () => props.priority,
  (newVal) => {
    if (newVal) {
      selectedPriority.value = priorities.value.find((p) => p.name === newVal)
    } else {
      selectedPriority.value = {
        name: "Select Priority",
        icon: "mdi-help-circle",
        color: "grey",
      }
    }
  },
  { immediate: true }
)

const selectPriority = (priority: Priority) => {
  selectedPriority.value = priority
  menu.value = false
  isMenuOpen.value = false
  emit("priority-selected", priority.name)
}

const filteredPriorities = computed(() => {
  return priorities.value.filter((p) =>
    p.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const toggleMenu = () => {
  menu.value = !menu.value
  if (!menu.value) {
    hoveredPriority.value = ""
  }
}

fetchPriorities()
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
        <v-btn class="text-subtitle-2 font-weight-regular" variant="text" v-bind="menu">
          <template v-slot:prepend>
            <v-icon size="small" :icon="selectedPriority.icon"></v-icon>
          </template>
          {{ selectedPriority.name }}
        </v-btn>
      </template>

      <v-card min-width="190" class="rounded-lg dispatch-side-card">
        <v-row no-gutters>
          <v-col align-self="start">
            <v-text-field
              v-model="searchQuery"
              label="Search priority..."
              density="compact"
              variant="solo"
              single-line
              hide-details
              flat
            >
              <template v-slot:label>
                <span class="text-subtitle-2 font-weight-regular"> Set priority to... </span>
              </template>
            </v-text-field>
          </v-col>
          <v-col align-self="end" cols="2" class="pb-2">
            <span class="hotkey">P</span>
          </v-col>
        </v-row>
        <v-divider></v-divider>
        <v-list lines="one">
          <v-list-item
            v-for="(priority, index) in filteredPriorities"
            :key="index"
            @click="selectPriority(priority)"
            @mouseover="hoveredPriority = priority.name"
            @mouseleave="hoveredPriority = ''"
            density="compact"
            rounded="lg"
            class="ml-1 mr-1"
            active-class="ma-4"
          >
            <template v-slot:prepend>
              <v-icon size="x-small" class="mr-n5" :color="priority.color">{{
                priority.icon
              }}</v-icon>
            </template>

            <v-list-item-title class="item-title-font">{{ priority.name }}</v-list-item-title>
            <template v-slot:append>
              <v-icon
                v-if="priority.name === selectedPriority.name"
                class="ml-2"
                size="x-small"
                :color="hoveredPriority === selectedPriority.name ? 'black' : ''"
              >
                mdi-check
              </v-icon>
            </template>
          </v-list-item>
        </v-list>
      </v-card>
    </v-menu>
  </div>
</template>

<style scoped>
.hotkey {
  vertical-align: baseline;
  text-transform: capitalize;
  text-align: center;
  color: rgba(0, 0, 0, 0.816);
  font-size: 11px;
  line-height: 110%;
  border-radius: 4px;
  padding-left: 4px;
  padding-right: 4px;
  padding-top: 1px;
  min-width: 17px;
  border: 0.5px solid rgb(216, 216, 216);
  background-color: rgb(254, 255, 254);
  box-shadow: rgba(0, 0, 0, 0.086) 0px 2px 0px 0px;
}

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
</style>
