<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, watchEffect, defineEmits, computed } from "vue"
import CasePriorityApi from "@/case/priority/api"
import type { Ref } from "vue"

type Status = {
  name: string
  icon: string
  color: string
}

const props = defineProps<{ status: string }>()

const menu: Ref<boolean> = ref(false)
const activator = ref(null) // A ref for the button acting as the activator
const statuses: Ref<Status[]> = ref([])
const selectedStatus: Ref<Status | null> = ref(null)
const searchQuery: Ref<string> = ref("")

statuses.value = [
  { name: "New", icon: "mdi-alert-circle", color: "grey" },
  { name: "Triage", icon: "mdi-alert-octagon", color: "blue" },
  { name: "Escalated", icon: "mdi-alert", color: "red" },
  { name: "Closed", icon: "mdi-check-circle", color: "green" },
]

const handleHotkey = (event: KeyboardEvent) => {
  if (event.key.toLowerCase() === "s" && !menu.value) {
    toggleMenu()
  }
}

onUnmounted(() => {
  window.removeEventListener("keyup", handleHotkey)
})

const emit = defineEmits(["status-selected"])

onMounted(() => {
  window.addEventListener("keyup", handleHotkey)
})

watch(selectedStatus, (newValue: Status | null) => {
  if (newValue && newValue.name !== props.status) {
    emit("status-selected", newValue.name)
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
  console.log("Toggled menu")
}
</script>

<template>
  <div>
    <div ref="activator">
      <v-btn
        class="text-subtitle-2 font-weight-regular"
        :prepend-icon="selectedStatus?.icon"
        variant="text"
        @click="toggleMenu"
        v-bind="$refs"
      >
        <template v-slot:prepend>
          <v-icon :color="selectedStatus.color"></v-icon>
        </template>
        {{ selectedStatus?.name }}
      </v-btn>
    </div>

    <v-menu v-model="menu" :close-on-content-click="false" :attach="activator">
      <v-card min-width="200" class="rounded-lg">
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
            <span class="text-subtitle-2 font-weight-regular"> Change status... </span>
            <span class="ml-11 hotkey">S</span>
          </template>
        </v-text-field>
        <v-divider></v-divider>
        <v-list lines="one">
          <v-list-item
            v-for="(status, index) in filteredStatuses"
            :key="index"
            @click="selectStatus(status)"
            density="compact"
            rounded="lg"
          >
            <template v-slot:prepend>
              <v-icon
                class="mr-n6 ml-n2"
                size="x-small"
                :icon="status.icon"
                :color="status.color"
              ></v-icon>
            </template>
            <v-list-item-title class="text-subtitle-2 font-weight-regular">{{
              status.name
            }}</v-list-item-title>
            <template v-slot:append>
              <v-icon v-if="status === selectedStatus" class="ml-2" size="x-small"
                >mdi-check</v-icon
              >
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
  padding: 2px;
  min-width: 17px;
  border: 0.5px solid rgb(216, 216, 216);
  background-color: rgb(254, 255, 254);
  box-shadow: rgba(0, 0, 0, 0.086) 0px 2px 0px 0px;
}
</style>
