<script setup lang="ts">
import { ref, onMounted, watch, computed } from "vue"
import { useSavingState } from "@/composables/useSavingState"
import IndividualApi from "@/individual/api"
import Hotkey from "@/atomics/Hotkey.vue"
import { useHotKey } from "@/composables/useHotkey"
import UserAvatar from "@/atomics/UserAvatar.vue"

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

interface Participant {
  name: string
  email: string
}

const store = useStore()
const { setSaving } = useSavingState()
const menu: Ref<boolean> = ref(false)
const participants: Ref<Participant[]> = ref([])
const selectedParticipant: Ref<string> = ref("")
const selectedParticipantEmail: Ref<string> = ref("")
const hoveredParticipant: Ref<string> = ref("")
const searchQuery: Ref<string> = ref("")

useHotKey([props.hotkey], () => {
  if (!menu.value) {
    toggleMenu()
  }
})

const emit = defineEmits(["participant-selected"])

// Fetch participants with their emails
const fetchParticipants = async (query = "") => {
  try {
    const options = {
      filter: JSON.stringify([
        { and: [{ model: "IndividualContact", field: "name", op: "ilike", value: `%${query}%` }] },
      ]),
      itemsPerPage: 10,
    }
    const response = await IndividualApi.getAll(options)
    participants.value = response.data.items.map((item: any) => ({
      name: item.name,
      email: item.email || "",
    }))
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

// Fetch email for a specific participant by name
const fetchParticipantEmail = async (name) => {
  if (!name || name === "Select assignee" || name === "Select reporter") {
    return ""
  }

  try {
    const response = await IndividualApi.getAll({
      filter: JSON.stringify([
        { and: [{ model: "IndividualContact", field: "name", op: "==", value: name }] },
      ]),
    })

    if (response.data.items.length > 0) {
      const individual = response.data.items[0]
      const email = individual.email || ""
      return email
    } else {
      return ""
    }
  } catch (error) {
    console.error(`[DEBUG] Error fetching email for participant ${name}:`, error)
    return ""
  }
}

onMounted(async () => {
  await fetchParticipants()

  // If we have an initial participant from props, fetch their email
  if (
    props.participant &&
    props.participant !== "Select assignee" &&
    props.participant !== "Select reporter"
  ) {
    const email = await fetchParticipantEmail(props.participant)
    selectedParticipantEmail.value = email
  }
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

    // Update the selected participant email
    selectedParticipantEmail.value = individual.email || ""

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
  async (newVal) => {
    if (newVal) {
      selectedParticipant.value = newVal

      // Directly fetch the email for this participant
      const email = await fetchParticipantEmail(newVal)
      selectedParticipantEmail.value = email
    } else {
      selectedParticipant.value = props.type === "assignee" ? "Select assignee" : "Select reporter"
      selectedParticipantEmail.value = ""
    }
  },
  { immediate: true }
)

const selectParticipant = (participant: Participant) => {
  selectedParticipant.value = participant.name
  selectedParticipantEmail.value = participant.email
  menu.value = false
}

const filteredParticipants = computed(() => {
  const lowerCaseQuery = searchQuery.value.toLowerCase()

  // If searching, only include participants that match the query
  if (lowerCaseQuery) {
    const otherParticipants = participants.value
      .filter((p) => p.name.toLowerCase().includes(lowerCaseQuery))
      .slice(0, 10)

    // Check if the selected participant matches the search query
    const isSelectedParticipantIncluded = otherParticipants.some(
      (p) => p.name === selectedParticipant.value
    )

    // If not included, add to the top of the list
    if (
      selectedParticipant.value &&
      !isSelectedParticipantIncluded &&
      selectedParticipant.value.toLowerCase().includes(lowerCaseQuery)
    ) {
      otherParticipants.unshift({
        name: selectedParticipant.value,
        email: selectedParticipantEmail.value,
      })
    }

    return otherParticipants
  }

  // If not searching, include all participants
  const selectedParticipantItem = selectedParticipant.value
    ? [
        {
          name: selectedParticipant.value,
          email: selectedParticipantEmail.value,
        },
      ]
    : []

  const otherParticipants = participants.value
    .filter((p) => p.name !== selectedParticipant.value)
    .slice(0, 9) // Adjust this number if you want more items in the list

  return [...selectedParticipantItem, ...otherParticipants]
})

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
                <UserAvatar
                  v-if="
                    selectedParticipant !== 'Select assignee' &&
                    selectedParticipant !== 'Select reporter'
                  "
                  :name="selectedParticipant"
                  :email="selectedParticipantEmail"
                  :size="14"
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
            v-for="(participant, index) in filteredParticipants"
            :key="index"
            @click="selectParticipant(participant)"
            @mouseover="hoveredParticipant = participant.name"
            @mouseleave="hoveredParticipant = ''"
            density="compact"
            rounded="lg"
            class="ml-1 mr-1"
            active-class="ma-4"
          >
            <template #prepend>
              <UserAvatar
                class="mr-2"
                :name="participant.name"
                :email="participant.email"
                :size="12"
              />
            </template>
            <v-list-item-title class="dispatch-text-title">
              {{ participant.name }}
            </v-list-item-title>
            <template #append>
              <v-icon
                v-if="participant.name === selectedParticipant"
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
