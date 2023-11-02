<template>
  <v-dialog v-model="showHandoffDialog" persistent max-width="800px">
    <v-card>
      <v-card-title>
        <span class="text-h5">Handoff Incidents</span>
      </v-card-title>
      <v-card-text> Select the new commander for the selected incidents. </v-card-text>
      <v-card-actions>
        <v-container>
          <v-row>
            <v-col cols="12">
              <participant-select
                v-model="commander"
                label="Incident Commander"
                :project="project"
              />
            </v-col>
            <!-- <v-col cols="12"> -->
            <!--   <v-checkbox v-model="report" label="Generate Report"/> -->
            <!-- </v-col> -->
            <v-btn color="blue en-1" variant="text" @click="closeHandoffDialog()"> Cancel </v-btn>
            <v-btn
              color="red en-1"
              variant="text"
              :loading="loading"
              @click="saveBulk({ commander: commander })"
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

import ParticipantSelect from "@/components/ParticipantSelect.vue"

export default {
  name: "IncidentHandoffDialog",

  data() {
    return {
      commander: { individual: { name: "Commander Name" } },
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
