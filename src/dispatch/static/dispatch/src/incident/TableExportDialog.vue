<template>
  <v-dialog v-model="showExport" persistent max-width="800px">
    <template v-slot:activator="{ on }">
      <v-btn color="secondary" class="ml-2" v-on="on"> Export </v-btn>
    </template>
    <v-card>
      <v-card-title>
        <span class="headline">Export Incidents</span>
      </v-card-title>
      <v-stepper v-model="e1">
        <v-stepper-header>
          <v-stepper-step :complete="e1 > 1" step="1" editable> Filter Data </v-stepper-step>
          <v-divider />
          <v-stepper-step :complete="e1 > 2" step="2" editable> Select Fields </v-stepper-step>
          <v-divider />
          <v-stepper-step step="3" editable> Preview </v-stepper-step>
        </v-stepper-header>
        <v-stepper-items>
          <v-stepper-content step="1">
            <v-list dense>
              <v-list-item>
                <v-list-item-content>
                  <incident-window-input v-model="reported_at" label="Reported At" />
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <project-combobox v-model="project" label="Projects" />
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <tag-filter-auto-complete v-model="tag" label="Tags" />
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <tag-type-filter-combobox v-model="tag_type" label="Tag Types" />
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
            <v-spacer />
            <v-btn @click="closeExport()" text> Cancel </v-btn>
            <v-btn color="info" @click="e1 = 2"> Continue </v-btn>
          </v-stepper-content>
          <v-stepper-content step="2">
            <v-autocomplete
              v-model="selectedFields"
              :items="allFields"
              label="Fields"
              multiple
              chips
              return-object
            />
            <v-spacer />
            <v-btn @click="closeExport()" text> Cancel </v-btn>
            <v-btn color="info" @click="e1 = 3"> Continue </v-btn>
          </v-stepper-content>
          <v-stepper-content step="3">
            <v-data-table
              hide-default-footer
              :headers="selectedFields"
              :items="items"
              :loading="previewRowsLoading"
            >
              <template v-slot:item.incident_priority.name="{ item }">
                <incident-priority :priority="item.incident_priority.name" />
              </template>
              <template v-slot:item.status="{ item }">
                <incident-status :status="item.status" :id="item.id" />
              </template>
            </v-data-table>
            <v-spacer />
            <v-btn @click="closeExport()" text> Cancel </v-btn>
            <v-badge :value="total" overlap color="info" bordered :content="total">
              <v-btn color="info" @click="exportToCSV()" :loading="exportLoading"> Export </v-btn>
            </v-badge>
          </v-stepper-content>
        </v-stepper-items>
      </v-stepper>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import SearchUtils from "@/search/utils"
import Util from "@/util"

import IncidentApi from "@/incident/api"
import IncidentPriority from "@/incident/IncidentPriority.vue"
import IncidentPriorityCombobox from "@/incident_priority/IncidentPriorityCombobox.vue"
import IncidentStatus from "@/incident/IncidentStatus.vue"
import IncidentStatusMultiSelect from "@/incident/IncidentStatusMultiSelect.vue"
import IncidentTypeCombobox from "@/incident_type/IncidentTypeCombobox.vue"
import IncidentWindowInput from "@/incident/IncidentWindowInput.vue"
import ProjectCombobox from "@/project/ProjectCombobox.vue"
import TagFilterAutoComplete from "@/tag/TagFilterAutoComplete.vue"
import TagTypeFilterCombobox from "@/tag_type/TagTypeFilterCombobox.vue"

export default {
  name: "IncidentTableExportDialog",

  components: {
    IncidentPriority,
    IncidentPriorityCombobox,
    IncidentStatus,
    IncidentStatusMultiSelect,
    IncidentTypeCombobox,
    IncidentWindowInput,
    ProjectCombobox,
    TagFilterAutoComplete,
    TagTypeFilterCombobox,
  },

  data() {
    return {
      e1: 1,
      selectedFields: [
        { text: "Name", value: "name", sortable: false },
        { text: "Title", value: "title", sortable: false },
        { text: "Description", value: "description", sortable: false },
        { text: "Resolution", value: "resolution", sortable: false },
        { text: "Status", value: "status", sortable: false },
        { text: "Incident Type", value: "incident_type.name", sortable: false },
        { text: "Incident Priority", value: "incident_priority.name", sortable: false },
      ],
      allFields: [
        { text: "Name", value: "name", sortable: false },
        { text: "Title", value: "title", sortable: false },
        { text: "Status", value: "status", sortable: false },
        { text: "Total Cost", value: "total_cost", sortable: false },
        { text: "Visibility", value: "visibility", sortable: false },
        { text: "Description", value: "description", sortable: false },
        { text: "Resolution", value: "resolution", sortable: false },
        { text: "Incident Type", value: "incident_type.name", sortable: false },
        { text: "Incident Priority", value: "incident_priority.name", sortable: false },
        { text: "Reporter", value: "reporter.individual.email", sortable: false },
        { text: "Commander", value: "commander.individual.email", sortable: false },
        { text: "Reporters Location", value: "reporters_location", sortable: false },
        { text: "Commanders Location", value: "commanders_location", sortable: false },
        { text: "Participants Location", value: "participants_location", sortable: false },
        { text: "Participants Team", value: "participants_team", sortable: false },
        { text: "Reported At", value: "reported_at", sortable: false },
        { text: "Stable At", value: "stable_at", sortable: false },
        { text: "Closed At", value: "closed_at", sortable: false },
        { text: "Incident Document Weblink", value: "incident_document.weblink", sortable: false },
        {
          text: "Incident Review Document Weblink",
          value: "incident_review_document.weblink",
          sortable: false,
        },
        { text: "Storage Weblink", value: "storage.weblink", sortable: false },
      ],
      previewRowsLoading: false,
      exportLoading: false,
    }
  },

  computed: {
    ...mapFields("incident", [
      "table.options.filters.incident_type",
      "table.options.filters.incident_priority",
      "table.options.filters.project",
      "table.options.filters.status",
      "table.options.filters.tag_type",
      "table.options.filters.tag",
      "table.options.filters.reported_at",
      "table.options",
      "table.rows.items",
      "table.rows.total",
      "dialogs.showExport",
    ]),
  },

  methods: {
    ...mapActions("incident", ["getAll", "closeExport"]),

    getPreviewData() {
      this.previewRowsLoading = "error"
      this.getAll({ itemsPerPage: 10 })
      this.previewRowsLoading = false
    },

    exportToCSV() {
      let params = SearchUtils.createParametersFromTableOptions({ ...this.options })

      params["itemsPerPage"] = -1
      params["include"] = this.selectedFields.map((item) => item.value)

      this.exportLoading = true

      return IncidentApi.getAll(params)
        .then((response) => {
          let items = response.data.items
          Util.exportCSV(items, "incident-details-export.csv")
          this.exportLoading = false
          this.closeExport()
        })
        .catch(() => {
          this.exportLoading = false
          this.closeExport()
        })
    },
  },

  created() {
    this.$watch(
      (vm) => [
        vm.incident_type,
        vm.incident_priority,
        vm.status,
        vm.project,
        vm.tag,
        vm.tag_type,
        vm.reported_at,
      ],
      () => {
        this.getPreviewData()
      }
    )
  },
}
</script>
