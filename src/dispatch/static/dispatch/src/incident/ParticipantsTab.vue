<template>
  <div>
    <remove-participant-dialog />
    <div v-if="participants && participants.length">
      <div class="d-flex align-center mb-3 ml-4 mr-4">
        <participant-select
          v-model="selectedParticipant"
          label="Add Participant"
          :project="project"
          class="flex-grow-1 mr-2"
        />
        <v-btn color="info" variant="flat" @click="addParticipants">Add</v-btn>
      </div>
      <div class="d-flex align-center mb-3 ml-4">
        <v-switch
          v-model="showInactive"
          label="Show inactive participants"
          density="compact"
          hide-details
        />
      </div>

      <span v-for="participant in filteredParticipants" :key="participant.id">
        <v-list-item class="my-3">
          <v-list-item-title>
            {{ participant.individual.name }} ({{ activeRoles(participant.participant_roles) }})
            <v-btn
              :href="participant.individual.weblink"
              target="_blank"
              icon
              variant="text"
              size="x-small"
              class="ml-2"
            >
              <v-icon size="small">mdi-open-in-new</v-icon>
            </v-btn>
          </v-list-item-title>
          <v-list-item-subtitle>
            {{ participant.team }} - {{ participant.location }}
          </v-list-item-subtitle>

          <template #append>
            <v-btn
              v-if="activeRoles(participant.participant_roles) !== 'Inactive'"
              @click="showRemoveParticipantDialog(participant)"
              icon
              variant="text"
              size="small"
            >
              <v-icon>mdi-delete</v-icon>
            </v-btn>
          </template>
        </v-list-item>
        <v-divider />
      </span>
    </div>
    <div v-else>
      <p class="text-center">No participant data available.</p>
    </div>
  </div>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { activeRoles } from "@/filters"
import IncidentApi from "@/incident/api"
import ParticipantSelect from "@/components/ParticipantSelect.vue"
import RemoveParticipantDialog from "@/incident/RemoveParticipantDialog.vue"

export default {
  name: "IncidentParticipantsTab",

  components: {
    ParticipantSelect,
    RemoveParticipantDialog,
  },

  setup() {
    return { activeRoles }
  },

  data() {
    return {
      showInactive: false,
      selectedParticipant: null,
    }
  },


  computed: {
    ...mapFields("incident", ["selected.participants", "selected.id", "selected.project"]),

    filteredParticipants() {
      if (!this.participants) return []

      if (this.showInactive) {
        // Show only inactive participants (all roles renounced)
        return this.participants.filter(participant => {
          if (!participant.participant_roles || participant.participant_roles.length === 0) {
            return false
          }
          // Check if participant has NO active roles (all roles renounced)
          return participant.participant_roles.every(role => role.renounced_at)
        })
      }

      // Show only active participants (at least one role not renounced)
      return this.participants.filter(participant => {
        if (!participant.participant_roles || participant.participant_roles.length === 0) {
          return false
        }
        // Check if participant has at least one active role (renounced_at is null)
        return participant.participant_roles.some(role => !role.renounced_at)
      })
    }
  },

  methods: {
    showRemoveParticipantDialog(participant) {
      this.$store.dispatch("incident/showRemoveParticipantDialog", participant)
    },

    async addParticipants() {
      if (!this.selectedParticipant || !Array.isArray(this.selectedParticipant) || this.selectedParticipant.length === 0) {
        console.log("No participants selected")
        return
      }

      try {
        // Add each selected participant
        for (const participant of this.selectedParticipant) {
          console.log("Adding participant:", participant.individual.email)
          await IncidentApi.addParticipant(this.id, participant.individual.email)
        }

        // Clear the selection
        this.selectedParticipant = null

        // Refresh the incident data to update the participants list
        // Small delay to allow background task to complete
        await new Promise(resolve => setTimeout(resolve, 1200))
        this.$store.dispatch("incident/get", this.id)
      } catch (error) {
        console.error("Error adding participants:", error)
      }
    },
  },
}
</script>
