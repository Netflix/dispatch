<template>
  <v-dialog v-model="showHandoffDialog" persistent max-width="800px">
    <v-card>
      <v-card-title>
        <span class="text-h5">Handoff Cases</span>
      </v-card-title>
      <v-card-text> Select the new assignee for the selected cases. </v-card-text>
      <v-card-actions>
        <v-container>
          <v-row>
            <v-col cols="12">
              <participant-select v-model="assignee" label="Case Assignee" :project="project" />
            </v-col>
            <v-btn color="blue en-1" variant="text" @click="closeHandoffDialog()"> Cancel </v-btn>
            <v-btn
              color="red en-1"
              variant="text"
              :loading="loading"
              @click="saveBulk({ assignee: assignee })"
            >
              Handoff
            </v-btn>
          </v-row>
        </v-container>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import ParticipantSelect from "@/incident/ParticipantSelect.vue"

export default {
  name: "CaseHandoffDialog",

  data() {
    return {
      assignee: { individual: { name: "Assignee Name" } },
    }
  },

  components: {
    ParticipantSelect,
  },

  computed: {
    ...mapFields("case_management", [
      "dialogs.showHandoffDialog",
      "selected.loading",
      "selected.project",
    ]),
  },

  methods: {
    ...mapActions("case_management", ["closeHandoffDialog", "saveBulk", "resetSelected"]),
  },
}
</script>
