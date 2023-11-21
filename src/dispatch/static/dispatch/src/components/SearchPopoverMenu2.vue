<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, watchEffect, defineEmits, computed, inject } from "vue"
import CasePriorityApi from "@/case/priority/api"
import type { Ref } from "vue"

const props = defineProps<{ priority: string }>()

const menu: Ref<boolean> = ref(false)
const activator = ref(null) // A ref for the button acting as the activator
const priorities: Ref<string[]> = ref([])
const selectedPriority: Ref<string> = ref("")
const searchQuery: Ref<string> = ref("")
const isMenuOpen: Ref<boolean> = inject("isMenuOpen")

const handleHotkey = (event) => {
  if (event.key.toLowerCase() === "p" && !menu.value && !isMenuOpen.value) {
    toggleMenu()
    isMenuOpen.value = true
  }
}

// Fetch priorities
const fetchPriorities = async () => {
  try {
    const response = await CasePriorityApi.getAll()
    priorities.value = response.data.items.map((item: any) => item.name)
  } catch (error) {
    console.error("Error fetching priorities:", error)
  }
}

onUnmounted(() => {
  window.removeEventListener("keyup", handleHotkey)
})

const emit = defineEmits(["priority-selected"])

onMounted(() => {
  fetchPriorities()
  window.addEventListener("keyup", handleHotkey)
})

watch(selectedPriority, (newValue: string) => {
  if (newValue && newValue !== props.priority) {
    emit("priority-selected", newValue)
  }
})

watch(
  () => props.priority,
  (newVal) => {
    if (newVal) {
      selectedPriority.value = newVal
    } else {
      selectedPriority.value = "Select Priority"
    }
  },
  { immediate: true }
)

const selectPriority = (priority: string) => {
  selectedPriority.value = priority
  menu.value = false
  isMenuOpen.value = false
}

const filteredPriorities = computed(() => {
  return priorities.value.filter((p) => p.toLowerCase().includes(searchQuery.value.toLowerCase()))
})

const toggleMenu = () => {
  menu.value = !menu.value
  if (!menu.value) {
    isMenuOpen.value = false
  }
  console.log("Toggled menu")
}
</script>

<template>
  <div>
    <div ref="activator">
      <v-btn
        class="text-subtitle-2 font-weight-regular"
        prepend-icon="mdi-check-circle"
        variant="text"
        @click="toggleMenu"
        v-bind="$refs"
      >
        {{ selectedPriority }}
      </v-btn>
    </div>

    <v-menu v-model="menu" :close-on-content-click="false" :attach="activator">
      <v-card min-width="200" class="rounded-lg">
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
            <span class="text-subtitle-2 font-weight-regular"> Set priority... </span>
            <span class="ml-11 hotkey">P</span>
          </template>
        </v-text-field>
        <v-divider></v-divider>
        <v-list lines="one">
          <v-list-item
            v-for="(priority, index) in filteredPriorities"
            :key="index"
            @click="selectPriority(priority)"
            density="compact"
            rounded="lg"
          >
            <template v-slot:prepend>
              <v-icon class="mr-n6 ml-n2" size="x-small" icon="mdi-priority-high"></v-icon>
            </template>
            <v-list-item-title class="text-subtitle-2 font-weight-regular">{{
              priority
            }}</v-list-item-title>
            <template v-slot:append>
              <v-icon v-if="priority === selectedPriority" class="ml-2" size="x-small"
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
