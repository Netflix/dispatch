<template>
  <v-dialog v-model="showExport" persistent max-width="800px">
    <template #activator="{ props }">
      <v-btn color="secondary" class="ml-2" v-bind="props"> Export </v-btn>
    </template>
    <v-card>
      <v-card-title>
        <span class="text-h5">Export Incidents</span>
      </v-card-title>
      <v-stepper v-model="e1">
        <v-stepper-header>
          <v-stepper-item :complete="e1 > 1" :value="1" editable> Filter Data </v-stepper-item>
          <v-divider />
          <v-stepper-item :complete="e1 > 2" :value="2" editable> Select Fields </v-stepper-item>
          <v-divider />
          <v-stepper-item :value="3" editable> Preview </v-stepper-item>
        </v-stepper-header>
        <v-stepper-window>
          <v-stepper-window-item :value="1">
            <div class="scrollable-container">
              <v-list density="compact">
                <v-list-item>
                  <date-window-input v-model="reported_at" label="Reported At" />
                </v-list-item>
                <v-list-item>
                  <project-combobox v-model="project" label="Projects" />
                </v-list-item>
                <v-list-item>
                  <tag-filter-auto-complete
                    v-model="tag"
                    label="Tags"
                    model="incident"
                    :project="project"
                  />
                </v-list-item>
                <v-list-item>
                  <tag-type-filter-combobox v-model="tag_type" label="Tag Types" />
                </v-list-item>
                <v-list-item>
                  <incident-type-combobox v-model="incident_type" />
                </v-list-item>
                <v-list-item>
                  <incident-severity-combobox v-model="incident_severity" />
                </v-list-item>
                <v-list-item>
                  <incident-priority-combobox v-model="incident_priority" />
                </v-list-item>
                <v-list-item>
                  <incident-status-multi-select v-model="status" />
                </v-list-item>
              </v-list>
              <v-spacer />
              <v-btn @click="closeExport()" variant="text"> Cancel </v-btn>
              <v-btn color="info" @click="e1 = 2"> Continue </v-btn>
            </div>
          </v-stepper-window-item>
          <v-stepper-window-item :value="2">
            <div class="scrollable-container">
              <v-autocomplete
                v-model="selectedFields"
                :items="allFields"
                item-title="text"
                label="Fields"
                multiple
                chips
                return-object
              />
              <v-spacer />
              <v-btn @click="closeExport()" variant="text"> Cancel </v-btn>
              <v-btn color="info" @click="e1 = 3"> Continue </v-btn>
            </div>
          </v-stepper-window-item>
          <v-stepper-window-item :value="3">
            <div class="scrollable-container">
              <v-data-table
                hide-default-footer
                :headers="selectedFields"
                :items="items"
                :loading="previewRowsLoading"
              >
                <template #item.incident_severity.name="{ item }">
                  <incident-severity :severity="item.incident_severity.name" />
                </template>
                <template #item.incident_priority.name="{ item }">
                  <incident-priority :priority="item.incident_priority.name" />
                </template>
                <template #item.status="{ item }">
                  <incident-status :status="item.status" :id="item.id" />
                </template>
              </v-data-table>
              <v-spacer />
              <v-btn @click="closeExport()" variant="text"> Cancel </v-btn>
              <v-badge :model-value="!!total" color="info" bordered :content="total">
                <v-btn color="info" @click="exportToCSV()" :loading="exportLoading"> Export </v-btn>
              </v-badge>
            </div>
          </v-stepper-window-item>
        </v-stepper-window>
      </v-stepper>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import SearchUtils from "@/search/utils"
import Util from "@/util"

import DateWindowInput from "@/components/DateWindowInput.vue"
import IncidentApi from "@/incident/api"
import IncidentPriority from "@/incident/priority/IncidentPriority.vue"
import IncidentPriorityCombobox from "@/incident/priority/IncidentPriorityCombobox.vue"
import IncidentSeverity from "@/incident/severity/IncidentSeverity.vue"
import IncidentSeverityCombobox from "@/incident/severity/IncidentSeverityCombobox.vue"
import IncidentStatus from "@/incident/status/IncidentStatus.vue"
import IncidentStatusMultiSelect from "@/incident/status/IncidentStatusMultiSelect.vue"
import IncidentTypeCombobox from "@/incident/type/IncidentTypeCombobox.vue"
import ProjectCombobox from "@/project/ProjectCombobox.vue"
import TagFilterAutoComplete from "@/tag/TagPicker.vue"
import TagTypeFilterCombobox from "@/tag_type/TagTypeFilterCombobox.vue"

export default {
  name: "IncidentTableExportDialog",

  components: {
    DateWindowInput,
    IncidentPriority,
    IncidentPriorityCombobox,
    IncidentSeverity,
    IncidentSeverityCombobox,
    IncidentStatus,
    IncidentStatusMultiSelect,
    IncidentTypeCombobox,
    ProjectCombobox,
    TagFilterAutoComplete,
    TagTypeFilterCombobox,
  },

  data() {
    return {
      e1: 1,
      selectedFields: [
        { text: "Name", title: "Name", key: "name", value: "name", sortable: false },
        { text: "Title", title: "Title", key: "title", value: "title", sortable: false },
        {
          text: "Description",
          title: "Description",
          key: "description",
          value: "description",
          sortable: false,
        },
        {
          text: "Resolution",
          title: "Resolution",
          key: "resolution",
          value: "resolution",
          sortable: false,
        },
        { text: "Status", title: "Status", key: "status", value: "status", sortable: false },
        {
          text: "Incident Type",
          title: "Incident Type",
          key: "incident_type.name",
          value: "incident_type.name",
          sortable: false,
        },
        {
          text: "Incident Severity",
          title: "Incident Severity",
          key: "incident_severity.name",
          value: "incident_severity.name",
          sortable: false,
        },
      ],
      allFields: [
        { text: "Name", title: "Name", key: "name", value: "name", sortable: false },
        {
          text: "Title",
          title: "Title",
          key: "title",
          value: "title",
          sortable: false,
        },
        { text: "Status", title: "Status", key: "status", value: "status", sortable: false },
        {
          text: "Total Cost",
          title: "Total Cost",
          key: "total_cost",
          value: "total_cost",
          sortable: false,
        },
        {
          text: "Visibility",
          title: "Visibility",
          key: "visibility",
          value: "visibility",
          sortable: false,
        },
        {
          text: "Description",
          title: "Description",
          key: "description",
          value: "description",
          sortable: false,
        },
        {
          text: "Resolution",
          title: "Resolution",
          key: "resolution",
          value: "resolution",
          sortable: false,
        },
        {
          text: "Incident Type",
          title: "Incident Type",
          key: "incident_type.name",
          value: "incident_type.name",
          sortable: false,
        },
        {
          text: "Incident Severity",
          title: "Incident Severity",
          key: "incident_severity.name",
          value: "incident_severity.name",
          sortable: false,
        },
        {
          text: "Incident Priority",
          title: "Incident Priority",
          key: "incident_priority.name",
          value: "incident_priority.name",
          sortable: false,
        },
        {
          text: "Reporter",
          title: "Reporter",
          key: "reporter.individual.email",
          value: "reporter.individual.email",
          sortable: false,
        },
        {
          text: "Commander",
          title: "Commander",
          key: "commander.individual.email",
          value: "commander.individual.email",
          sortable: false,
        },
        {
          text: "Reporters Location",
          title: "Reporters Location",
          key: "reporters_location",
          value: "reporters_location",
          sortable: false,
        },
        {
          text: "Commanders Location",
          title: "Commanders Location",
          key: "commanders_location",
          value: "commanders_location",
          sortable: false,
        },
        {
          text: "Participants Location",
          title: "Participants Location",
          key: "participants_location",
          value: "participants_location",
          sortable: false,
        },
        {
          text: "Participants Team",
          title: "Participants Team",
          key: "participants_team",
          value: "participants_team",
          sortable: false,
        },
        {
          text: "Reported At",
          title: "Reported At",
          key: "reported_at",
          value: "reported_at",
          sortable: false,
        },
        {
          text: "Stable At",
          title: "Stable At",
          key: "stable_at",
          value: "stable_at",
          sortable: false,
        },
        {
          text: "Closed At",
          title: "Closed At",
          key: "closed_at",
          value: "closed_at",
          sortable: false,
        },
        {
          text: "Incident Document Weblink",
          title: "Incident Document Weblink",
          key: "incident_document.weblink",
          value: "incident_document.weblink",
          sortable: false,
        },
        {
          text: "Incident Review Document Weblink",
          title: "Incident Review Document Weblink",
          key: "incident_review_document.weblink",
          value: "incident_review_document.weblink",
          sortable: false,
        },
        {
          text: "Storage Weblink",
          title: "Storage Weblink",
          key: "storage.weblink",
          value: "storage.weblink",
          sortable: false,
        },
      ],
      previewRowsLoading: false,
      exportLoading: false,
    }
  },

  computed: {
    ...mapFields("incident", [
      "dialogs.showExport",
      "table.options",
      "table.options.filters.incident_priority",
      "table.options.filters.incident_severity",
      "table.options.filters.incident_type",
      "table.options.filters.project",
      "table.options.filters.reported_at",
      "table.options.filters.status",
      "table.options.filters.tag",
      "table.options.filters.tag_type",
      "table.rows.items",
      "table.rows.total",
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
          const fieldOrder = this.selectedFields.map((field) => field.value)
          Util.exportCSVOrdered(items, "incident-details-export.csv", fieldOrder)
          this.exportLoading = false
          this.closeExport()
        })
        .catch((error) => {
          console.log(error)
          this.exportLoading = false
          this.closeExport()
        })
    },
  },

  created() {
    this.$watch(
      (vm) => [
        vm.incident_priority,
        vm.incident_severity,
        vm.incident_type,
        vm.project,
        vm.reported_at,
        vm.status,
        vm.tag,
        vm.tag_type,
      ],
      () => {
        this.getPreviewData()
      }
    )
  },
}
</script>

<style scoped>
.scrollable-container {
  max-height: 60vh; /* Adjust as needed */
  overflow-y: auto;
}
</style>
