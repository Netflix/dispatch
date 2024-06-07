<script setup lang="ts">
import { ref, onMounted, watch, computed } from "vue"
import { useSavingState } from "@/composables/useSavingState"
import IndividualApi from "@/individual/api"
import Hotkey from "@/atomics/Hotkey.vue"
import { useHotKey } from "@/composables/useHotkey"

import DTooltip from "@/components/DTooltip.vue"
import type { Ref } from "vue"
import { useStore } from "vuex"
import CaseApi from "@/case/api"

const props = withDefaults(
  defineProps<{
    participant: string
    hotkey: string
    label: string
    tooltipLabel: string
    type: string
    hotkeys: string[]
  }>(),
  {
    hotkey: "a",
  }
)

const store = useStore()
const { setSaving } = useSavingState()
const menu: Ref<boolean> = ref(false)
const participants: Ref<string[]> = ref([])
const selectedParticipant: Ref<string> = ref("")
const hoveredParticipant: Ref<string> = ref("")
const searchQuery: Ref<string> = ref("")

useHotKey([props.hotkey], () => {
  if (!menu.value) {
    toggleMenu()
  }
})

const emit = defineEmits(["participant-selected"])

// Fetch priorities
const fetchParticipants = async (query = "") => {
  try {
    const options = {
      filter: JSON.stringify([
        { and: [{ model: "IndividualContact", field: "name", op: "ilike", value: `%${query}%` }] },
      ]),
      itemsPerPage: 10,
    }
    const response = await IndividualApi.getAll(options)
    participants.value = response.data.items.map((item: any) => item.name)
  } catch (error) {
    console.error("Error fetching participants:", error)
  }
}

watch(
  searchQuery,
  async (newValue: string) => {
    await fetchParticipants(newValue)
  },
  { immediate: true }
)

onMounted(() => {
  fetchParticipants()
})

watch(selectedParticipant, async (newValue: string) => {
  if (newValue && newValue !== props.participant) {
    // Emit the participant-selected event with the participant name
    emit("participant-selected", newValue)

    // Fetch the participant object from the API
    const response = await IndividualApi.getAll({
      filter: JSON.stringify([
        { and: [{ model: "IndividualContact", field: "name", op: "==", value: newValue }] },
      ]),
    })

    const individual = response.data.items[0]

    // Check if the participant was found
    if (!individual) {
      console.error(`No individual found with name ${newValue}`)
      return
    }

    // Get the case details from the Vuex store
    const caseDetails = store.state.case_management.selected

    // Depending on the type of participant, update the respective field in the case details
    if (props.type === "assignee") {
      caseDetails.assignee.individual = individual
    } else if (props.type === "reporter") {
      caseDetails.reporter.individual = individual
    }

    setSaving(true)
    try {
      await CaseApi.update(caseDetails.id, caseDetails)
    } catch (error) {
      console.error("Error updating case:", error)
    }
    setSaving(false)
  }
})

watch(
  () => props.participant,
  (newVal) => {
    if (newVal) {
      selectedParticipant.value = newVal
    } else {
      selectedParticipant.value = props.type === "assignee" ? "Select assignee" : "Select reporter"
    }
  },
  { immediate: true }
)

const selectParticipant = (participant: string) => {
  selectedParticipant.value = participant
  menu.value = false
}

const filteredParticipants = computed(() => {
  const lowerCaseQuery = searchQuery.value.toLowerCase()

  // If searching, only include participants that match the query
  if (lowerCaseQuery) {
    const otherParticipants = participants.value
      .filter((p) => p.toLowerCase().includes(lowerCaseQuery))
      .slice(0, 10)

    // Check if the selected participant matches the search query
    const isSelectedParticipantIncluded = otherParticipants.includes(selectedParticipant.value)

    // If not included, add to the top of the list
    if (
      selectedParticipant.value &&
      !isSelectedParticipantIncluded &&
      selectedParticipant.value.toLowerCase().includes(lowerCaseQuery)
    ) {
      otherParticipants.unshift(selectedParticipant.value)
    }

    return otherParticipants
  }

  // If not searching, include all participants
  const selectedParticipantItem = selectedParticipant.value ? [selectedParticipant.value] : []
  const otherParticipants = participants.value
    .filter((p) => p !== selectedParticipant.value)
    .slice(0, 9) // Adjust this number if you want more items in the list

  return [...selectedParticipantItem, ...otherParticipants]
})

// Function to generate a hue from a string
const getAvatarGradient = (participant: string) => {
  let hash = 5381
  for (let i = 0; i < participant.length; i++) {
    hash = ((hash << 5) + hash) ^ participant.charCodeAt(i) // Using XOR operator for better distribution
  }

  const hue = Math.abs(hash) % 360 // Ensure hue is a positive number
  const fromColor = `hsl(${hue}, 95%, 50%)`
  const toColor = `hsl(${(hue + 120) % 360}, 95%, 50%)` // Getting triadic color by adding 120 to hue

  return `linear-gradient(${fromColor}, ${toColor})`
}

const toggleMenu = () => {
  menu.value = !menu.value
  if (!menu.value) {
    hoveredParticipant.value = ""
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
        <DTooltip :text="props.tooltipLabel" :hotkeys="[hotkey.toUpperCase()]">
          <template #activator="{ tooltip }">
            <v-btn
              class="menu-activator text-subtitle-2 font-weight-regular"
              variant="text"
              v-bind="{ ...tooltip, ...menuProps }"
            >
              <template #prepend>
                <v-avatar
                  v-if="
                    selectedParticipant !== 'Select assignee' &&
                    selectedParticipant !== 'Select reporter'
                  "
                  size="14px"
                  :style="{ background: getAvatarGradient(selectedParticipant) }"
                />
                <v-icon v-else size="14px">mdi-account-reactivate</v-icon>
                <!-- Show icon if selectedParticipant is default -->
              </template>
              <span style="font-size: 0.8125rem; font-weight: 500; color: rgb(60, 65, 73)">
                {{ selectedParticipant }}
              </span>
            </v-btn>
          </template>
        </DTooltip>
      </template>

      <v-card min-width="200" class="rounded-lg dispatch-side-card">
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
          <v-col align-self="end" cols="2" class="pb-2">
            <Hotkey :hotkey="props.hotkey.toUpperCase()" />
          </v-col>
        </v-row>
        <v-divider />
        <v-list lines="one">
          <v-list-item
            v-for="(filteredParticipant, index) in filteredParticipants"
            :key="index"
            @click="selectParticipant(filteredParticipant)"
            @mouseover="hoveredParticipant = filteredParticipant"
            @mouseleave="hoveredParticipant = ''"
            density="compact"
            rounded="lg"
            class="ml-1 mr-1"
            active-class="ma-4"
          >
            <template #prepend>
              <v-avatar
                class="mr-n2"
                size="12px"
                :style="{ background: getAvatarGradient(filteredParticipant) }"
              />
              <!-- <v-icon class="mr-n6 ml-n2" size="x-small" icon="mdi-account"></v-icon> -->
            </template>
            <v-list-item-title class="dispatch-text-title">
              {{ filteredParticipant }}
            </v-list-item-title>
            <template #append>
              <v-icon
                v-if="filteredParticipant === selectedParticipant"
                class="ml-2"
                size="x-small"
                :color="hoveredParticipant === selectedParticipant ? 'black' : ''"
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
