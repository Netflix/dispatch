<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, watchEffect, defineEmits, computed } from "vue"
import IndividualApi from "@/individual/api"
import type { Ref } from "vue"

const props = defineProps<{ participant: string }>()

const menu: Ref<boolean> = ref(false)
const activator = ref(null) // A ref for the button acting as the activator
const participants: Ref<string[]> = ref([])
const selectedParticipant: Ref<string> = ref("")
const hoveredParticipant: Ref<string> = ref("")
const searchQuery: Ref<string> = ref("")

const handleHotkey = (event: KeyboardEvent) => {
  const key = event.key.toLowerCase()

  if (key === "a" && !menu.value) {
    toggleMenu()
  }

  if (key === "escape" && menu.value) {
    toggleMenu()
  }
}

onUnmounted(() => {
  window.removeEventListener("keyup", handleHotkey)
})

const emit = defineEmits(["participant-selected"])

// Fetch priorities
const fetchParticipants = async () => {
  try {
    const options = { itemsPerPage: -1 }
    const response = await IndividualApi.getAll(options)
    console.log("Got response for participants", response.data.items)
    participants.value = response.data.items.map((item: any) => item.name)
  } catch (error) {
    console.error("Error fetching participants:", error)
  }
}

onMounted(() => {
  fetchParticipants()
  window.addEventListener("keyup", handleHotkey)
})

watch(selectedParticipant, (newValue: string) => {
  if (newValue && newValue !== props.participant) {
    emit("participant-selected", newValue)
  }
})

watch(
  () => props.participant,
  (newVal) => {
    if (newVal) {
      selectedParticipant.value = newVal
    } else {
      selectedParticipant.value = "Select assignee"
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
  console.log("Toggled menu")
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
          class="text-subtitle-2 font-weight-regular"
          prepend-icon="mdi-account"
          variant="text"
          v-bind="menu"
        >
          <template v-slot:prepend>
            <v-avatar
              size="12px"
              :style="{ background: getAvatarGradient(selectedParticipant) }"
            ></v-avatar>
          </template>
          {{ selectedParticipant }}
        </v-btn>
      </template>

      <v-card min-width="200" class="rounded-lg dispatch-side-card">
        <v-row no-gutters>
          <v-col align-self="start">
            <v-text-field
              v-model="searchQuery"
              label="Search participant..."
              density="compact"
              variant="solo"
              single-line
              hide-details
              flat
            >
              <template v-slot:label>
                <span class="text-subtitle-2 font-weight-regular"> Assign to... </span>
              </template>
            </v-text-field>
          </v-col>
          <v-col align-self="end" cols="2" class="pb-2">
            <span class="hotkey">A</span>
          </v-col>
        </v-row>
        <v-divider></v-divider>
        <v-list lines="one">
          <v-list-item
            v-for="(participant, index) in filteredParticipants"
            :key="index"
            @click="selectParticipant(participant)"
            @mouseover="hoveredParticipant = participant"
            @mouseleave="hoveredParticipant = ''"
            density="compact"
            rounded="lg"
            active-class="ma-4"
          >
            <template v-slot:prepend>
              <v-avatar
                class="mr-n2"
                size="12px"
                :style="{ background: getAvatarGradient(participant) }"
              ></v-avatar>
              <!-- <v-icon class="mr-n6 ml-n2" size="x-small" icon="mdi-account"></v-icon> -->
            </template>
            <v-list-item-title class="item-title-font">{{ participant }}</v-list-item-title>
            <template v-slot:append>
              <v-icon
                v-if="participant === selectedParticipant"
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
