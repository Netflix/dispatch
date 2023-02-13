<template>
  <v-dialog v-model="showHandoffDialog" persistent max-width="800px">
    <v-card>
      <v-card-title>
        <span class="headline">Handoff Incidents</span>
      </v-card-title>
      <v-card-text>
        Select the new commander for the selected incidents.
      </v-card-text>
      <v-card-actions>
        <v-container grid-list-md>
          <v-layout wrap>
            <v-flex xs12>
              <participant-select v-model="commander" label="Incident Commander" :project="project"/>
            </v-flex>
            <!-- <v-flex xs12> -->
            <!--   <v-checkbox v-model="report" label="Generate Report"/> -->
            <!-- </v-flex> -->
            <v-btn color="blue en-1" text @click="closeHandoffDialog()"> Cancel </v-btn>
            <v-btn color="red en-1" text :loading="loading" @click="saveBulk({commander: commander})">
              Handoff
            </v-btn>
          </v-layout>
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
  name: "IncidentHandoffDialog",

  data() {
    return {
      commander: { individual: { name: "Commander Name" }},
      report: false,
    }
  },

  components: {
    ParticipantSelect,
  },

  computed: {
    ...mapFields("incident", ["dialogs.showHandoffDialog", "selected.loading", "selected.project"]),
  },

  methods: {
    ...mapActions("incident", ["closeHandoffDialog", "saveBulk", "resetSelected"]),
  },
}
</script>
