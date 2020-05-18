<template>
  <div>
    <div v-if="participants">
      <span v-for="participant in participants" :key="participant.id">
        <v-list-item :href="participant.individual.weblink" target="_blank">
          <v-list-item-content>
            <v-list-item-title>
              {{ participant.individual.name }} ({{
                participant.participant_roles | commaString("role")
              }})
            </v-list-item-title>
            <v-list-item-subtitle>
              {{ participant.team }} - {{ participant.location }}
            </v-list-item-subtitle>
          </v-list-item-content>
          <v-list-item-action>
            <v-list-item-icon>
              <v-icon>open_in_new</v-icon>
            </v-list-item-icon>
          </v-list-item-action>
        </v-list-item>
        <v-divider />
      </span>
    </div>
    <div v-else>
      No participant data available.
    </div>
  </div>
</template>

<script>
import { mapFields } from "vuex-map-fields"

export default {
  name: "IncidentParticipantsTab",
  computed: {
    ...mapFields("incident", ["selected.participants"])
  }
}
</script>
