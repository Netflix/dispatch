<template>
  <v-dialog v-model="showPreviewDialog" persistent max-width="800px">
    <v-card>
      <v-card-title>
        <span class="text-h5">Preview Incident Participants</span>
      </v-card-title>
      <v-card-text>
        <v-container>
          The list of designated participants for when this incident is created. This functions as a
          checkpoint to ensure only the intended individuals are involved when the incident is
          opened.
          <incident-participants-tab />
        </v-container>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="blue en-1" variant="text" @click="closePreviewDialog()"> Cancel </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { activeRoles } from "@/filters"
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import IncidentParticipantsTab from "@/incident/ParticipantsTab.vue"
export default {
  name: "IncidentPreviewDialog",
  components: {
    IncidentParticipantsTab,
  },
  setup() {
    return { activeRoles }
  },
  computed: {
    ...mapFields("incident", ["dialogs.showPreviewDialog", "selected.participants"]),
  },
  methods: {
    ...mapActions("incident", ["closePreviewDialog"]),
  },
}
</script>
