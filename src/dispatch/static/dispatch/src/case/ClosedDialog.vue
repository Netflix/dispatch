<template>
  <v-dialog v-model="showClosedDialog" persistent max-width="800px">
    <v-card>
      <v-card-title>
        <span class="text-h5">Close Cases</span>
      </v-card-title>
      <v-card-text>
        Closed cased require a resolution reason and a resolution summary.
      </v-card-text>
      <v-card-actions>
        <v-container>
          <v-row>
            <v-col cols="12">
              <v-select
                v-model="resolutionReason"
                label="Resolution Reason"
                :items="resolutionReasons"
                hint="The general reason why a given case was resolved."
              />
            </v-col>
            <v-col cols="12">
              <v-label class="mb-2">Resolution</v-label>
              <v-card flat color="grey-lighten-5" class="rounded-lg">
                <RichEditor
                  :content="resolution"
                  @update:model-value="(newValue) => (resolution = newValue)"
                  placeholder="Description of the actions taken to resolve the case..."
                  style="min-height: 150px; margin: 10px; font-size: 0.9125rem; font-weight: 400"
                />
              </v-card>
              <v-messages
                :value="['Description of the actions taken to resolve the case.']"
                class="v-messages--hint"
              />
            </v-col>
            <v-btn color="blue en-1" variant="text" @click="closeClosedDialog()"> Cancel </v-btn>
            <v-btn
              color="red en-1"
              variant="text"
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
          </v-row>
        </v-container>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import RichEditor from "@/components/RichEditor.vue"

export default {
  name: "CaseClosedDialog",

  components: {
    RichEditor,
  },

  data() {
    return {
      resolutionReason: "False Positive",
      resolution: "Description of the actions taken to resolve the case.",
      resolutionReasons: ["False Positive", "User Acknowledged", "Mitigated", "Escalated"],
    }
  },

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
