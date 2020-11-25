<template>
  <v-dialog v-model="showExport" persistent max-width="800px">
    <template v-slot:activator="{ on }">
      <v-btn color="secondary" dark v-on="on">Export</v-btn>
    </template>
    <v-card>
      <v-card-title>
        <span class="headline">Export Incidents</span>
      </v-card-title>
      <v-stepper v-model="e1">
        <v-stepper-header>
          <v-stepper-step :complete="e1 > 1" step="1" editable>
            Select Filters
          </v-stepper-step>
          <v-divider></v-divider>

          <v-stepper-step :complete="e1 > 2" step="2" editable>
            Select Fields
          </v-stepper-step>

          <v-divider></v-divider>

          <v-stepper-step step="3" editable>
            Preview Export
          </v-stepper-step>
        </v-stepper-header>

        <v-stepper-items>
          <v-stepper-content step="1">
            <v-list dense>
              <v-list-item>
                <v-list-item-content>
                  <tag-filter-combobox v-model="tag" label="Tags" />
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <incident-type-combobox v-model="incident_type" />
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <incident-priority-combobox v-model="incident_priority" />
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <incident-status-multi-select v-model="status" />
                </v-list-item-content>
              </v-list-item>
            </v-list>
            <v-btn color="primary" @click="e1 = 2">
              Continue
            </v-btn>

            <v-btn text>
              Cancel
            </v-btn>
          </v-stepper-content>

          <v-stepper-content step="2">
            <v-combobox v-model="select" :items="fields" label="Fields" multiple chips></v-combobox>
            <v-btn color="primary" @click="e1 = 3">
              Continue
            </v-btn>

            <v-btn text>
              Cancel
            </v-btn>
          </v-stepper-content>

          <v-stepper-content step="3">
            <v-btn color="primary" @click="e1 = 1">
              Export
            </v-btn>

            <v-btn text>
              Cancel
            </v-btn>
          </v-stepper-content>
        </v-stepper-items>
      </v-stepper>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"
import IncidentStatusMultiSelect from "@/incident/IncidentStatusMultiSelect.vue"
import TagFilterCombobox from "@/tag/TagFilterCombobox.vue"
import IncidentTypeCombobox from "@/incident_type/IncidentTypeCombobox.vue"
import IncidentPriorityCombobox from "@/incident_priority/IncidentPriorityCombobox.vue"
export default {
  name: "IncidentTableExportDialog",
  data() {
    return {
      e1: 1,
      select: ["name", "title", "status"],
      items: [
        "name",
        "title",
        "status",
        "cost",
        "incident_type.name",
        "incident_priority.name",
        "reporter.email",
        "commander.email",
        "primary_team",
        "primary_location"
      ]
    }
  },
  components: {
    // IndividualCombobox,
    TagFilterCombobox,
    IncidentTypeCombobox,
    IncidentPriorityCombobox,
    IncidentStatusMultiSelect
  },
  computed: {
    ...mapFields("incident", [
      "table.options.filters.commander",
      "table.options.filters.reporter",
      "table.options.filters.incident_type",
      "table.options.filters.incident_priority",
      "table.options.filters.status",
      "table.options.filters.tag",
      "dialogs.showExport"
    ])
  },

  methods: {
    ...mapActions("incident", ["exportIncidents", "closeExport"])
  }
}
</script>
