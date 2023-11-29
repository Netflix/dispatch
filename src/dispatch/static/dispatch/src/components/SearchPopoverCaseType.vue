<script setup lang="ts">
import { ref, watch, defineEmits, computed, inject } from "vue"
import CaseTypeApi from "@/case/type/api"
import { useHotKey } from "@/composables/useHotkey"
import type { Ref } from "vue"

type CaseType = {
  name: string
}

const props = defineProps<{ caseType: string }>()

const menu: Ref<boolean> = ref(false)
const caseTypes: Ref<CaseType[]> = ref([])
const hoveredCaseType: Ref<string> = ref("")
const selectedCaseType: Ref<CaseType | null> = computed(() => {
  return (
    caseTypes.value.find((p) => p.name === props.caseType) || {
      name: "Select Priority",
    }
  )
})
const searchQuery: Ref<string> = ref("")
const isMenuOpen: Ref<boolean> = inject("isMenuOpen")

useHotKey(["c"], () => {
  if (!menu.value) {
    toggleMenu()
  }
})

const fetchTypes = async () => {
  try {
    const response = await CaseTypeApi.getAll()
    caseTypes.value = response.data.items.map((item: any) => item.name)
  } catch (error) {
    console.error("Error fetching priorities:", error)
  }
}

const emit = defineEmits(["priority-selected"])

watch(
  () => props.caseType,
  (newVal) => {
    if (newVal) {
      selectedCaseType.value = caseTypes.value.find((p) => p.name === newVal)
    } else {
      selectedCaseType.value = {
        name: "Select Priority",
      }
    }
  },
  { immediate: true }
)

const selectPriority = (priority: Priority) => {
  selectedCaseType.value = priority
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

fetchTypes()
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
