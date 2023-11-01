<template>
  <div>
    <div v-if="participants && participants.length">
      <span v-for="participant in participants" :key="participant.id">
        <v-list-item :href="participant.individual.weblink" target="_blank" class="my-3">
          <v-list-item-title>
            {{ participant.individual.name }} ({{ activeRoles(participant.participant_roles) }})
          </v-list-item-title>
          <v-list-item-subtitle>
            {{ participant.team }} - {{ participant.location }}
          </v-list-item-subtitle>

          <template #append>
            <v-icon>mdi-open-in-new</v-icon>
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

export default {
  name: "IncidentParticipantsTab",

  setup() {
    return { activeRoles }
  },

  computed: {
    ...mapFields("incident", ["selected.participants"]),
  },
}
</script>
