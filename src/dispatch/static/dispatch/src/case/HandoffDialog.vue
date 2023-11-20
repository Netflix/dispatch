<template>
  <v-dialog v-model="showHandoffDialog" persistent max-width="800px">
    <v-form @submit.prevent v-slot="{ isValid }">
      <v-card>
        <v-card-title>
          <span class="text-h5">Handoff Cases</span>
        </v-card-title>
        <v-card-text> Select the new assignee for the selected cases. </v-card-text>
        <v-card-actions>
          <v-container>
            <v-row>
              <v-col cols="12">
                <participant-select
                  v-model="assignee"
                  label="Case Assignee"
                  :project="project"
                  :rules="[required_and_only_one]"
                />
              </v-col>
              <v-btn color="blue en-1" variant="text" @click="closeHandoffDialog()"> Cancel </v-btn>
              <v-btn
                color="red en-1"
                variant="text"
                :loading="loading"
                :disabled="!isValid.value"
                @click="saveBulk({ assignee: assignee[0] })"
              >
                Handoff
              </v-btn>
            </v-row>
          </v-container>
        </v-card-actions>
      </v-card>
    </v-form>
  </v-dialog>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import ParticipantSelect from "@/components/ParticipantSelect.vue"

export default {
  name: "CaseHandoffDialog",

  data() {
    return {
      assignee: null,
      project: null,
      required_and_only_one: (value) => {
        if (!value || value.length == 0) {
          return "This field is required"
        }
        if (value && value.length > 1) {
          return "Only one is allowed"
        }
        return true
      },
    }
  },

  components: {
    ParticipantSelect,
  },

  computed: {
    ...mapFields("case_management", [
      "dialogs.showHandoffDialog",
      "selected.loading",
      "table.rows.selected",
    ]),
  },

  methods: {
    ...mapActions("case_management", ["closeHandoffDialog", "saveBulk", "resetSelected"]),
  },

  watch: {
    selected(val) {
      this.project = val.map((i) => i.project)
    },
  },

  created: function () {
    this.project = this.selected.map((i) => i.project)
  },
}
</script>
