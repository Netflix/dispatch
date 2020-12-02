<template>
  <v-dialog v-model="showExport" persistent max-width="800px">
    <template v-slot:activator="{ on }">
      <v-btn color="secondary" class="ml-2" dark v-on="on">Export</v-btn>
    </template>
    <v-card>
      <v-card-title>
        <span class="headline">Export Incidents</span>
      </v-card-title>
      <v-stepper v-model="e1">
        <v-stepper-header>
          <v-stepper-step :complete="e1 > 1" step="1" editable>
            Filter Data
          </v-stepper-step>
          <v-divider></v-divider>

          <v-stepper-step :complete="e1 > 2" step="2" editable>
            Select Fields
          </v-stepper-step>

          <v-divider></v-divider>

          <v-stepper-step step="3" editable>
            Preview
          </v-stepper-step>
        </v-stepper-header>

        <v-stepper-items>
          <v-stepper-content step="1">
            <v-list dense>
              <v-list-item>
                <v-list-item-content>
                  <tag-filter-combobox v-model="filters.tag" label="Tags" />
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <incident-type-combobox v-model="filters.incident_type" />
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <incident-priority-combobox v-model="filters.incident_priority" />
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <incident-status-multi-select v-model="filters.status" />
                </v-list-item-content>
              </v-list-item>
            </v-list>
            <v-btn color="primary" @click="e1 = 2">
              Continue
            </v-btn>

            <v-btn @click="closeExport()" text>
              Cancel
            </v-btn>
          </v-stepper-content>

          <v-stepper-content step="2">
            <v-autocomplete
              v-model="selectedFields"
              :items="allFields"
              label="Fields"
              multiple
              chips
              return-object
            ></v-autocomplete>
            <v-btn color="primary" @click="e1 = 3">
              Continue
            </v-btn>

            <v-btn @click="closeExport()" text>
              Cancel
            </v-btn>
          </v-stepper-content>

          <v-stepper-content step="3">
            <v-data-table
              hide-default-footer
              :headers="selectedFields"
              :items="previewRows.items"
              :loading="previewRowsLoading"
            >
            </v-data-table>
            <v-badge :value="previewRows.total" overlap bordered :content="previewRows.total">
              <v-btn color="primary" @click="exportToCSV()" :loading="exportLoading">
                Export
              </v-btn>
            </v-badge>

            <v-btn @click="closeExport()" text>
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
import { forEach, each, has } from "lodash"
import { mapActions } from "vuex"
import IncidentApi from "@/incident/api"
import IncidentStatusMultiSelect from "@/incident/IncidentStatusMultiSelect.vue"
import TagFilterCombobox from "@/tag/TagFilterCombobox.vue"
import IncidentTypeCombobox from "@/incident_type/IncidentTypeCombobox.vue"
import IncidentPriorityCombobox from "@/incident_priority/IncidentPriorityCombobox.vue"
export default {
  name: "IncidentTableExportDialog",
  data() {
    return {
      e1: 1,
      selectedFields: [
        { text: "Name", value: "name", sortable: false },
        { text: "Title", value: "title", sortable: false },
        { text: "Status", value: "status", sortable: false },
        { text: "Incident Type", value: "incident_type.name", sortable: false },
        { text: "Incident Priority", value: "incident_priority.name", sortable: false }
      ],
      allFields: [
        { text: "Name", value: "name", sortable: false },
        { text: "Title", value: "title", sortable: false },
        { text: "Status", value: "status", sortable: false },
        { text: "Cost", value: "cost", sortable: false },
        { text: "Visibility", value: "visibility", sortable: false },
        { text: "Incident Type", value: "incident_type.name", sortable: false },
        { text: "Incident Priority", value: "incident_priority.name", sortable: false },
        { text: "Reporter", value: "reporter.email", sortable: false },
        { text: "Commander", value: "commander.email", sortable: false },
        { text: "Primary Team", value: "primary_team", sortable: false },
        { text: "Primary Location", value: "primary_location", sortable: false },
        { text: "Reported At", value: "reported_at", sortable: false },
        { text: "Stable At", value: "stable_at", sortable: false },
        { text: "Closed At", value: "closed_at", sortable: false },
        { text: "Incident Document Weblink", value: "incident_document.weblink", sortable: false },
        {
          text: "Incident Review Document Weblink",
          value: "incident_review_document.weblink",
          sortable: false
        },
        { text: "Storage Weblink", value: "storage.weblink", sortable: false }
      ],
      previewRows: {
        items: [],
        total: null
      },
      previewRowsLoading: false,
      filters: {
        incident_type: null,
        incident_priority: null,
        status: null,
        tag: null
      },
      exportLoading: false
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
    ...mapFields("incident", ["dialogs.showExport"])
  },

  methods: {
    ...mapActions("incident", ["closeExport"]),

    formatTableOptions(filters) {
      let tableOptions = {}

      tableOptions.fields = []
      tableOptions.ops = []
      tableOptions.values = []

      forEach(filters, function(value, key) {
        each(value, function(value) {
          if (has(value, "id")) {
            tableOptions.fields.push(key + ".id")
            tableOptions.values.push(value.id)
          } else {
            tableOptions.fields.push(key)
            tableOptions.values.push(value)
          }
          tableOptions.ops.push("==")
        })
      })
      return tableOptions
    },

    getPreviewData() {
      let tableOptions = this.formatTableOptions(this.filters)
      this.previewRowsLoading = true
      return IncidentApi.getAll(tableOptions).then(response => {
        this.previewRows = response.data
        this.previewRowsLoading = false
      })
    },

    exportToCSV() {
      let tableOptions = this.formatTableOptions(this.filters)
      tableOptions["itemsPerPage"] = -1
      tableOptions["include"] = this.selectedFields.map(item => item.value)
      this.exportLoading = true
      return IncidentApi.getAll(tableOptions)
        .then(response => {
          let items = response.data.items

          let csvContent = "data:text/csv;charset=utf-8,"
          csvContent += [
            Object.keys(items[0]).join(","),
            ...items.map(item => {
              return Object.values(item)
                .map(value => {
                  if (typeof value === "object") {
                    return value[Object.keys(value)[0]]
                  }
                  return value
                })
                .join(",")
            })
          ]
            .join("\n")
            .replace(/(^\[)|(\]$)/gm, "")

          const data = encodeURI(csvContent)
          const link = document.createElement("a")
          link.setAttribute("href", data)
          link.setAttribute("download", "incidentExport.csv")
          link.click()
          this.exportLoading = false
          this.closeExport()
        })
        .catch(() => {
          this.exportLoading = false
          this.closeExport()
        })
    }
  },
  mounted() {
    this.$watch(
      vm => [
        vm.filters.incident_type,
        vm.filters.incident_priority,
        vm.filters.status,
        vm.filters.tag
      ],
      () => {
        this.getPreviewData()
      }
    )
  }
}
</script>
