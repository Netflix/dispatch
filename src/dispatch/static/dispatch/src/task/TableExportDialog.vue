<template>
  <v-dialog v-model="showExport" persistent max-width="800px">
    <template v-slot:activator="{ on }">
      <v-btn color="secondary" class="ml-2" v-on="on">Export</v-btn>
    </template>
    <v-card>
      <v-card-title>
        <span class="headline">Export Tasks</span>
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
                  <incident-combobox v-model="filters.incident" />
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <task-status-multi-select v-model="filters.status" />
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <incident-type-combobox v-model="filters.incident_type" label="Incident Type" />
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <incident-priority-combobox
                    v-model="filters.incident_priority"
                    label="Incident Priority"
                  />
                </v-list-item-content>
              </v-list-item>
            </v-list>
            <v-btn color="info" @click="e1 = 2">
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
            <v-btn color="info" @click="e1 = 3">
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
              <template v-slot:item.description="{ item }">
                <div class="text-truncate" style="max-width: 400px">
                  {{ item.description }}
                </div>
              </template>
              <template v-slot:item.incident.status="{ item }">
                <incident-status :status="item.incident.status" :id="item.id" />
              </template>
              <template v-slot:item.incident_priority.name="{ item }">
                <incident-priority :priority="item.incident.incident_priority.name" />
              </template>
              <template v-slot:item.creator.individual_contact.name="{ item }">
                <participant :participant="item.creator" />
              </template>
              <template v-slot:item.owner.individual_contact.name="{ item }">
                <participant :participant="item.owner" />
              </template>
              <template v-slot:item.incident_type.name="{ item }">
                {{ item.incident.incident_type.name }}
              </template>
              <template v-slot:item.tickets="{ item }">
                <a
                  v-for="ticket in item.tickets"
                  :key="ticket.weblink"
                  :href="ticket.weblink"
                  target="_blank"
                  style="text-decoration: none;"
                >
                  Ticket
                  <v-icon small>open_in_new</v-icon>
                </a>
              </template>
              <template v-slot:item.assignees="{ item }">
                <participant
                  v-for="assignee in item.assignees"
                  :key="assignee.id"
                  :participant="assignee"
                >
                </participant>
              </template>
              <template v-slot:item.resolve_by="{ item }">{{
                item.resolve_by | formatDate
              }}</template>
              <template v-slot:item.created_at="{ item }">{{
                item.created_at | formatDate
              }}</template>
              <template v-slot:item.resolved_at="{ item }"
                >{{ item.resolved_at | formatDate }}
              </template>
              <template v-slot:item.source="{ item }">
                {{ item.source }}
                <a :href="item.weblink" target="_blank" style="text-decoration: none;"> </a>
              </template>
            </v-data-table>
            <v-badge
              :value="previewRows.total"
              overlap
              color="info"
              bordered
              :content="previewRows.total"
            >
              <v-btn color="info" @click="exportToCSV()" :loading="exportLoading">
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
import TaskApi from "@/task/api"
import IncidentCombobox from "@/incident/IncidentCombobox.vue"
import IncidentTypeCombobox from "@/incident_type/IncidentTypeCombobox.vue"
import IncidentPriorityCombobox from "@/incident_priority/IncidentPriorityCombobox.vue"
import TaskStatusMultiSelect from "@/task/TaskStatusMultiSelect.vue"
import IncidentStatus from "@/incident/IncidentStatus.vue"
import IncidentPriority from "@/incident/IncidentPriority.vue"
import Participant from "@/incident/Participant.vue"

export default {
  name: "TaskTableExportDialog",
  data() {
    return {
      e1: 1,
      selectedFields: [
        { text: "Incident Name", value: "incident.name", sortable: false },
        { text: "Incident Priority", value: "incident_priority.name", sortable: false },
        { text: "Incident Status", value: "incident.status", sortable: false },
        { text: "Incident Type", value: "incident_type.name", sortable: false },
        { text: "Status", value: "status", sortable: false },
        { text: "Creator", value: "creator.individual_contact.name", sortable: false },
        { text: "Owner", value: "owner.individual_contact.name", sortable: false },
        { text: "Assignees", value: "assignees", sortable: false }
      ],
      allFields: [
        { text: "Incident Name", value: "incident.name", sortable: false },
        { text: "Incident Priority", value: "incident_priority.name", sortable: false },
        { text: "Incident Status", value: "incident.status", sortable: false },
        { text: "Incident Type", value: "incident_type.name", sortable: false },
        { text: "Status", value: "status", sortable: false },
        { text: "Creator", value: "creator.individual_contact.name", sortable: false },
        { text: "Owner", value: "owner.individual_contact.name", sortable: false },
        { text: "Assignees", value: "assignees", sortable: false },
        { text: "Description", value: "description", sortable: false },
        { text: "Source", value: "source", sortable: false },
        { text: "Tickets", value: "tickets", sortable: false },
        { text: "Due By", value: "resolve_by", sortable: true },
        { text: "Created At", value: "created_at", sortable: true },
        { text: "Resolved At", value: "resolved_at", sortable: true }
      ],
      previewRows: {
        items: [],
        total: null
      },
      previewRowsLoading: false,
      filters: {
        incident: null,
        incident_type: null,
        incident_priority: null,
        status: null
      },
      exportLoading: false
    }
  },
  components: {
    // IndividualCombobox,
    IncidentCombobox,
    IncidentTypeCombobox,
    IncidentPriorityCombobox,
    TaskStatusMultiSelect,
    IncidentStatus,
    IncidentPriority,
    Participant
  },
  computed: {
    ...mapFields("task", ["dialogs.showExport"])
  },

  methods: {
    ...mapActions("task", ["closeExport"]),

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
      this.previewRowsLoading = "error"
      return TaskApi.getAll(tableOptions).then(response => {
        this.previewRows = response.data
        this.previewRowsLoading = false
      })
    },

    exportToCSV() {
      let tableOptions = this.formatTableOptions(this.filters)
      tableOptions["itemsPerPage"] = -1
      tableOptions["include"] = this.selectedFields.map(item => item.value)
      this.exportLoading = true
      return TaskApi.getAll(tableOptions)
        .then(response => {
          let items = response.data.items

          let csvContent = "data:text/csv;charset=utf-8,"
          csvContent += [
            Object.keys(items[0]).join(","),
            ...items.map(item => {
              if (typeof item === "object") {
                return Object.values(item)
                  .map(value => {
                    if (value === null) {
                      return ""
                    }
                    if (typeof value === "object") {
                      return value[Object.keys(value)[0]]
                    }
                    return value
                  })
                  .join(",")
              }
              return ""
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
        .catch(err => {
          console.log(err)
          this.exportLoading = false
          this.closeExport()
        })
    }
  },
  mounted() {
    this.$watch(
      vm => [vm.filters.incident_type, vm.filters.incident_priority, vm.filters.status],
      () => {
        this.getPreviewData()
      }
    )
  }
}
</script>
