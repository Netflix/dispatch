<script setup lang="ts">
// First Party
import { ref, onMounted, watch, computed } from "vue"
import type { Ref } from "vue"
import { useStore } from "vuex"

// Composables
import { useSavingState } from "@/composables/useSavingState"
import { useHotKey } from "@/composables/useHotkey"

// Third Party
import CaseApi from "@/case/api"
import IndividualApi from "@/individual/api"
import { IndividualContact } from "@/individual/individualContact"
import Hotkey from "@/atomics/Hotkey.vue"
import ParticipantHoverCard from "@/participant/ParticipantHoverCard.vue"

const props = withDefaults(
  defineProps<{
    participant: IndividualContact
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

const defaultContact: IndividualContact = {
  name: "",
  email: "",
  company: null,
  contact_type: null,
  created_at: "",
  external_id: null,
  filters: [],
  id: 0,
  is_active: false,
  is_external: false,
  mobile_phone: null,
  notes: null,
  office_phone: null,
  owner: null,
  title: null,
  updated_at: "",
  weblink: "",
}

const store = useStore()
const { setSaving } = useSavingState()
const menu: Ref<boolean> = ref<boolean>(false)

const participants: Ref<IndividualContact[]> = ref<IndividualContact[]>([])
const selectedParticipant: Ref<IndividualContact | null> = ref<IndividualContact | null>(null)

const hoveredParticipant: Ref<string> = ref<string>("")
const searchQuery: Ref<string> = ref<string>("")

useHotKey([props.hotkey], () => {
  if (!menu.value) {
    toggleMenu()
  }
})

const emit = defineEmits(["participant-selected"])

/**
 * Fetches participants from the API and stores them in the participants ref.
 * If an error occurs during the fetch operation, it logs the error and shows a notification.
 */
const fetchParticipants = async () => {
  try {
    const options = { itemsPerPage: -1 }
    const response = await IndividualApi.getAll(options)
    // Store the entire participant objects
    participants.value = response.data.items
  } catch (error) {
    console.error("Error fetching participants:", error)

    store.commit(
      "notification_backend/addBeNotification",
      {
        text: `Failed to fetch participants.`,
        type: "exception",
      },
      { root: true }
    )
  }
}

onMounted(() => {
  fetchParticipants()
})

/**
 * Vue watcher function that reacts to changes in selectedParticipantName.
 * When the selected participant's name changes, this function emits an event,
 * fetches the participant's details from the API, and updates the case details accordingly.
 */
watch(selectedParticipant, async (newValue: IndividualContact | null) => {
  if (newValue && props.participant && newValue.name !== props.participant.name) {
    // Emit the participant-selected event with the participant name
    emit("participant-selected", newValue)

    // Get the case details from the Vuex store
    const caseDetails = store.state.case_management.selected

    // Depending on the type of participant, update the respective field in the case details
    if (props.type === "assignee") {
      caseDetails.assignee.individual = newValue
    } else if (props.type === "reporter") {
      caseDetails.reporter.individual = newValue
    }

    setSaving(true)
    try {
      await CaseApi.update(caseDetails.id, caseDetails)
    } catch (error) {
      console.error(`Failed to assign new participant ${newValue} to case`, error)
      store.commit(
        "notification_backend/addBeNotification",
        {
          text: `Failed to assign new participant ${newValue} to case`,
          type: "exception",
        },
        { root: true }
      )
    }
    setSaving(false)
  }
})

watch(
  () => props.participant,
  async (newVal) => {
    if (newVal && newVal.name) {
      selectedParticipant.value = newVal
    } else {
      selectedParticipant.value = {
        ...defaultContact,
        name: props.type === "assignee" ? "Select assignee" : "Select reporter",
      }
    }
  },
  { immediate: true }
)

const selectParticipant = (participant: IndividualContact) => {
  selectedParticipant.value = participant
  menu.value = false
}

/**
 * Returns participants whose name or email includes the query string.
 */
const filterParticipants = (participants: IndividualContact[], query: string) =>
  participants.filter(
    (p) => p.name.toLowerCase().includes(query) || p.email.toLowerCase().includes(query)
  )

/**
 * Checks if a participant's name or email matches the given query.
 */
const participantMatches = (participant: IndividualContact, query: string) =>
  participant.name === query || participant.email === query

/**
 * Adds the participant who matches the selectedParticipantName to the start of the participants array.
 */
const addMatchingParticipant = (
  participants: IndividualContact[],
  selectedParticipantName: string
) => {
  // If the matching participant already exists in the list, return the list as is
  if (participants.some((p) => participantMatches(p, selectedParticipantName))) {
    return participants
  }

  const participantMatch = participants.find((p) => participantMatches(p, selectedParticipantName))

  if (participantMatch) {
    participants.unshift(participantMatch)
  }
  return participants
}

/**
 * Computed property that returns an array of participants filtered on the basis of a search query.
 * If no query is provided, it returns the array of all participants with the selected participant at the start.
 */
const filteredParticipants = computed(() => {
  const lowerCaseQuery = searchQuery.value.toLowerCase()

  // If a search query is provided
  if (lowerCaseQuery) {
    // Filter participants who match the query
    let otherParticipants = filterParticipants(participants.value, lowerCaseQuery).slice(0, 10)

    // If a selected participant's name is provided, add the participant to the start of the array
    if (selectedParticipant.value.name) {
      otherParticipants = addMatchingParticipant(otherParticipants, selectedParticipant.value.name)
    }

    // Return the modified array of participants
    return otherParticipants
  }

  // If no search query is provided
  // Find the selected participant
  const selectedParticipantObject = participants.value.find(
    (p) => p.name === selectedParticipant.value.name
  )

  // If the selected participant is found, add it to the start of the array
  const selectedParticipantItem = selectedParticipantObject ? [selectedParticipantObject] : []

  // Get all other participants except the selected one
  const otherParticipants = participants.value
    .filter((p) => p.name !== selectedParticipant.value.name)
    .slice(0, 9) // Adjust this number if you want more items in the list

  // Return the array of participants with the selected participant at the start
  // This ensures that the selected participant is always the first item in the list
  return [...selectedParticipantItem, ...otherParticipants]
})

/**
 * Generates a linear gradient hue based on the participant's name.
 * This function uses a hashing function to generate a numeric hash from the participant's name.
 * This numeric hash is then converted into an HSL color gradient.
 */
const getAvatarGradient = (participantName: string) => {
  let hash = 5381

  // Generate the hash from the participant's name
  for (let i = 0; i < participantName.length; i++) {
    // Using XOR operator for better distribution
    hash = ((hash << 5) + hash) ^ participantName.charCodeAt(i)
  }

  // Ensure hue is a positive number in the range [0, 360)
  const hue = Math.abs(hash) % 360

  // Generate the starting and ending colors for the gradient
  const fromColor = `hsl(${hue}, 95%, 50%)`

  // Getting a triadic color by adding 120 to the hue
  const toColor = `hsl(${(hue + 120) % 360}, 95%, 50%)`

  // Return the linear gradient
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
        <ParticipantHoverCard :item="selectedParticipant">
          <v-btn
            class="menu-activator text-subtitle-2 font-weight-regular"
            variant="text"
            v-bind="{ ...menuProps }"
          >
            <template #prepend>
              <v-avatar
                v-if="
                  selectedParticipant.name !== 'Select assignee' &&
                  selectedParticipant.name !== 'Select reporter'
                "
                size="14px"
                :style="{ background: getAvatarGradient(selectedParticipant.name) }"
              />
              <v-icon v-else size="14px">mdi-account-reactivate</v-icon>
              <!-- Show icon if selectedParticipant is default -->
            </template>
            <span style="font-size: 0.8125rem; font-weight: 500; color: rgb(60, 65, 73)">
              {{ selectedParticipant.name }}
            </span>
          </v-btn>
        </ParticipantHoverCard>
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
            @mouseover="hoveredParticipant = filteredParticipant.name"
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
                :style="{ background: getAvatarGradient(filteredParticipant.name) }"
              />
              <!-- <v-icon class="mr-n6 ml-n2" size="x-small" icon="mdi-account"></v-icon> -->
            </template>
            <v-list-item-title class="dispatch-text-title list-item-title">
              {{ filteredParticipant.name }}
              <span class="text-medium-emphasis">({{ filteredParticipant.email }})</span>
            </v-list-item-title>
            <template #append>
              <v-icon
                v-if="filteredParticipant.name === selectedParticipant.name"
                class="ml-2"
                size="x-small"
                :color="hoveredParticipant === selectedParticipant.name ? 'black' : ''"
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
  border-radius: 4px;
}

.list-item-title {
  max-width: 200px;
  min-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
