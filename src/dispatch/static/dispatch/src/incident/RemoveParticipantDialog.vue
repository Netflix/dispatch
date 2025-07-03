<template>
  <v-dialog v-model="showRemoveParticipantDialog" persistent max-width="600px">
    <v-card>
      <v-card-title>
        <span class="text-h5">Remove Participant?</span>
      </v-card-title>
      <v-card-text>
        <v-container>
          <div v-if="participantToRemove">
            Are you sure you want to remove
            <strong>{{ participantToRemove.individual.name }}</strong> from this incident?
          </div>
        </v-container>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="blue en-1" variant="text" @click="closeRemoveParticipantDialog()">
          Cancel
        </v-btn>
        <v-btn color="red en-1" variant="text" @click="removeParticipant(selected)"> Remove </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

export default {
  name: "IncidentRemoveParticipantDialog",

  computed: {
    ...mapFields("incident", [
      "dialogs.showRemoveParticipantDialog",
      "dialogs.participantToRemove",
      "selected",
    ]),
  },

  methods: {
    ...mapActions("incident", ["closeRemoveParticipantDialog", "removeParticipant"]),
  },
}
</script>
