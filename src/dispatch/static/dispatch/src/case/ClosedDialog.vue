<template>
  <v-dialog v-model="showClosedDialog" persistent max-width="800px">
    <v-card>
      <v-card-title>
        <span class="headline">Close Cases</span>
      </v-card-title>
      <v-card-text>
        Closed cased require a resolution reason and a resolution summary.
      </v-card-text>
      <v-card-actions>
        <v-container grid-list-md>
          <v-layout wrap>
            <v-flex xs12>
              <v-select
                v-model="resolutionReason"
                label="Resolution Reason"
                :items="resolutionReasons"
                hint="The general reason why a given case was resolved."
              />
            </v-flex>
            <v-flex xs12>
              <v-textarea
                v-model="resolution"
                label="Resolution"
                hint="Description of the actions taken to resolve the case."
                clearable
              />
            </v-flex>
            <v-btn color="blue en-1" text @click="closeClosedDialog()"> Cancel </v-btn>
            <v-btn
              color="red en-1"
              text
              :loading="loading"
              @click="
                saveBulk({
                  resolution_reason: resolutionReason,
                  resolution: resolution,
                  status: 'Closed',
                })
              "
            >
              Close
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

export default {
  name: "CaseClosedDialog",

  data() {
    return {
      resolutionReason: null,
      resolution: null,
      resolutionReasons: ["False Positive", "User Acknowledged", "Mitigated", "Escalated"],
    }
  },

  components: {},

  computed: {
    ...mapFields("case_management", [
      "dialogs.showClosedDialog",
      "selected.loading",
      "selected.project",
    ]),
  },

  methods: {
    ...mapActions("case_management", ["closeClosedDialog", "saveBulk", "resetSelected"]),
  },
}
</script>
