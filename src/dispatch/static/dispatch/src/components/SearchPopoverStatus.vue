<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, watchEffect, defineEmits, computed } from "vue"
import Hotkey from "@/atomics/Hotkey.vue"
import { useHotKey } from "@/composables/useHotkey"
import type { Ref } from "vue"
import { useStore } from "vuex"
import CaseApi from "@/case/api"

type Status = {
  name: string
  icon: string
  color: string
}

const props = defineProps<{ status: string }>()

const store = useStore()
const menu: Ref<boolean> = ref(false)
const statuses: Ref<Status[]> = ref([])
const selectedStatus: Ref<Status | null> = ref(null)
const hoveredStatus: Ref<string> = ref("")
const searchQuery: Ref<string> = ref("")

statuses.value = [
  { name: "New", icon: "mdi-alert-circle", color: "grey" },
  { name: "Triage", icon: "mdi-alert-octagon", color: "blue" },
  { name: "Closed", icon: "mdi-check-circle", color: "green" },
  { name: "Escalated", icon: "mdi-alert", color: "red" },
]

useHotKey(["s"], () => {
  if (!menu.value) {
    toggleMenu()
  }
})

const emit = defineEmits(["status-selected"])

watch(selectedStatus, (newValue: Status | null) => {
  if (newValue && newValue.name !== props.status) {
    emit("status-selected", newValue.name)

    // Get the case details from the Vuex store
    const caseDetails = store.state.case_management.selected

    // Update the status in the case details
    caseDetails.status = newValue.name

    // Call the CaseApi.update method to update the case details
    CaseApi.update(caseDetails.id, caseDetails)
      .then(() => console.log("Case details updated successfully"))
      .catch((e) => console.error("Failed to update case details", e))
  }
})

watch(
  () => props.status,
  (newVal) => {
    if (newVal) {
      selectedStatus.value = statuses.value.find((status) => status.name === newVal) || null
    } else {
      selectedStatus.value = null
    }
  },
  { immediate: true }
)

const selectStatus = (status: Status) => {
  selectedStatus.value = status
  menu.value = false
}

const filteredStatuses = computed(() => {
  return statuses.value.filter((s) =>
    s.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const toggleMenu = () => {
  menu.value = !menu.value
  if (!menu.value) {
    hoveredStatus.value = ""
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
        <v-btn class="text-subtitle-2 font-weight-regular" variant="text" v-bind="menu">
          <template v-slot:prepend>
            <v-icon size="small" :icon="selectedStatus.icon"></v-icon>
          </template>
          {{ selectedStatus.name }}
        </v-btn>
      </template>

      <v-card min-width="190" class="rounded-lg dispatch-side-card">
        <v-row no-gutters>
          <v-col align-self="start">
            <v-text-field
              v-model="searchQuery"
              label="Search status..."
              density="compact"
              variant="solo"
              single-line
              hide-details
              flat
            >
              <template v-slot:label>
                <span class="text-subtitle-2 font-weight-regular"> Set status to... </span>
              </template>
            </v-text-field>
          </v-col>
          <v-col align-self="end" cols="2" class="pb-2">
            <Hotkey hotkey="S" />
          </v-col>
        </v-row>
        <v-divider></v-divider>
        <v-list lines="one">
          <v-list-item
            v-for="(status, index) in filteredStatuses"
            :key="index"
            @click="selectStatus(status)"
            @mouseover="hoveredStatus = status.name"
            @mouseleave="hoveredStatus = ''"
            density="compact"
            rounded="lg"
            class="ml-1 mr-1"
            active-class="ma-4"
          >
            <template v-slot:prepend>
              <v-icon size="x-small" class="mr-n5" :color="status.color">{{ status.icon }}</v-icon>
            </template>

            <v-list-item-title class="item-title-font">{{ status.name }}</v-list-item-title>
            <template v-slot:append>
              <v-icon
                v-if="status.name === selectedStatus.name"
                class="ml-2"
                size="x-small"
                :color="hoveredStatus === selectedStatus.name ? 'black' : ''"
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
