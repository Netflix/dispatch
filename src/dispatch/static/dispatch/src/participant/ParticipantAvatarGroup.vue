<script setup>
import { ref, computed, watch } from "vue"
import { useHotKey } from "@/composables/useHotkey"

const props = defineProps({
  participants: {
    type: Array,
    required: true,
  },
  highlightedParticipants: {
    type: Array,
    default: () => [],
  },
})

const menu = ref(false)
let orderedParticipants = ref([])
const hoveredParticipant = ref("")
const searchQuery = ref("")

useHotKey(["Meta", "Shift", "p"], () => {
  if (!menu.value) {
    toggleMenu()
  }
})

watch(
  () => props.participants,
  (newVal) => {
    if (newVal) {
      const assignee = newVal.find((participant) =>
        props.highlightedParticipants.includes(participant.individual.name)
      )
      const otherParticipants = newVal.filter(
        (participant) => !props.highlightedParticipants.includes(participant.individual.name)
      )
      if (assignee) {
        orderedParticipants.value = [assignee, ...otherParticipants]
      } else {
        orderedParticipants.value = newVal
      }
    }
  },
  { immediate: true }
)

const visibleParticipants = computed(() => orderedParticipants.value.slice(0, 3))
// Correct the calculation of hiddenParticipants
const hiddenParticipants = computed(() => {
  if (orderedParticipants.value.length > 3) {
    return orderedParticipants.value.slice(3)
  } else {
    return []
  }
})
const filteredParticipants = computed(() => {
  const lowerCaseQuery = searchQuery.value.toLowerCase()

  // If searching, only include participants that match the query
  if (lowerCaseQuery) {
    return orderedParticipants.value.filter((p) =>
      p.individual.name.toLowerCase().includes(lowerCaseQuery)
    )
  }

  // If not searching, include all participants
  return orderedParticipants.value
})

const getAvatarGradient = (participant) => {
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
        <v-btn variant="text" v-bind="menuProps">
          <!-- Display Visible Participants -->
          <div class="avatar-row">
            <!-- Display +n Avatar -->
            <div v-if="hiddenParticipants.length > 0" class="avatar-container">
              <v-avatar size="20px" class="extra-avatar">
                +{{ hiddenParticipants.length }}
              </v-avatar>
            </div>
            <div
              v-for="(participant, index) in visibleParticipants"
              :key="index"
              class="avatar-container"
            >
              <v-avatar
                size="20px"
                :style="{ background: getAvatarGradient(participant.individual.name) }"
                v-on="on"
              />
            </div>
          </div>
        </v-btn>
      </template>
      <v-card min-width="255" class="rounded-lg dispatch-side-card">
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
            <template #prepend>
              <v-avatar
                class="mr-n2"
                size="12px"
                :style="{ background: getAvatarGradient(participant.individual.name) }"
              />
              <!-- <v-icon class="mr-n6 ml-n2" size="x-small" icon="mdi-account"></v-icon> -->
            </template>
            <v-list-item-title class="dispatch-text-title">
              {{ participant.individual.name }}
            </v-list-item-title>
          </v-list-item>
        </v-list>
      </v-card>
    </v-menu>
  </div>
</template>

<style lang="scss" scoped>
@import "@/styles/index.scss";

.avatar-row {
  display: flex;
  align-items: center;
  justify-content: start;
  flex-direction: row-reverse;
  position: relative;
}

.avatar-container {
  border: 2px solid white; /* Add a border around the avatar */
  border-radius: 50%; /* Make the border circular */
  position: relative;
  margin-right: -5px; /* Adjust this value to change the overlapping amount */
}

.extra-avatar {
  background-color: white;
  color: rgb(60, 65, 73);
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

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
</style>
