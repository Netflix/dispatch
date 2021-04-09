<template>
  <v-dialog v-model="showExport" persistent max-width="800px">
    <template v-slot:activator="{ on }">
      <v-btn color="secondary" class="ml-2" v-on="on"> Export </v-btn>
    </template>
    <v-card>
      <v-card-title>
        <span class="headline">Export Tasks</span>
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
                  <incident-combobox v-model="incident" />
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <project-combobox v-model="project" label="Projects" />
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <task-status-multi-select v-model="status" />
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <incident-type-combobox v-model="incident_type" label="Incident Type" />
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <incident-priority-combobox
                    v-model="incident_priority"
                    label="Incident Priority"
                  />
                </v-list-item-content>
              </v-list-item>
            </v-list>
            <v-btn color="info" @click="e1 = 2"> Continue </v-btn>

            <v-btn @click="closeExport()" text> Cancel </v-btn>
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
            <v-btn color="info" @click="e1 = 3"> Continue </v-btn>

            <v-btn @click="closeExport()" text> Cancel </v-btn>
          </v-stepper-content>

          <v-stepper-content step="3">
            <v-data-table
              hide-default-footer
              :headers="selectedFields"
              :items="items"
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
                  style="text-decoration: none"
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
                />
              </template>
              <template v-slot:item.resolve_by="{ item }">
                {{ item.resolve_by | formatDate }}
              </template>
              <template v-slot:item.created_at="{ item }">
                {{ item.created_at | formatDate }}
              </template>
              <template v-slot:item.resolved_at="{ item }">
                {{ item.resolved_at | formatDate }}
              </template>
              <template v-slot:item.source="{ item }">
                {{ item.source }}
                <a :href="item.weblink" target="_blank" style="text-decoration: none" />
              </template>
            </v-data-table>
            <v-badge :value="total" overlap color="info" bordered :content="total">
              <v-btn color="info" @click="exportToCSV()" :loading="exportLoading"> Export </v-btn>
            </v-badge>

            <v-btn @click="closeExport()" text> Cancel </v-btn>
          </v-stepper-content>
        </v-stepper-items>
      </v-stepper>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { mapActions } from "vuex"

import Util from "@/util"
import SearchUtils from "@/search/utils"

import TaskApi from "@/task/api"
import IncidentCombobox from "@/incident/IncidentCombobox.vue"
import IncidentTypeCombobox from "@/incident_type/IncidentTypeCombobox.vue"
import IncidentPriorityCombobox from "@/incident_priority/IncidentPriorityCombobox.vue"
import ProjectCombobox from "@/project/ProjectCombobox.vue"
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
        { text: "Creator", value: "creator.individual.email", sortable: false },
        { text: "Owner", value: "owner.individual.email", sortable: false },
        { text: "Assignees", value: "assignees[].individual.name", sortable: false },
      ],
      allFields: [
        { text: "Incident Name", value: "incident.name", sortable: false },
        { text: "Incident Priority", value: "incident_priority.name", sortable: false },
        { text: "Incident Status", value: "incident.status", sortable: false },
        { text: "Incident Type", value: "incident_type.name", sortable: false },
        { text: "Status", value: "status", sortable: false },
        { text: "Creator", value: "creator.individual.email", sortable: false },
        { text: "Owner", value: "owner.individual.email", sortable: false },
        { text: "Assignees", value: "assignees[].individual.email", sortable: false },
        { text: "Description", value: "description", sortable: false },
        { text: "Source", value: "source", sortable: false },
        { text: "Tickets", value: "tickets", sortable: false },
        { text: "Due By", value: "resolve_by", sortable: true },
        { text: "Created At", value: "created_at", sortable: true },
        { text: "Resolved At", value: "resolved_at", sortable: true },
      ],
      previewRowsLoading: false,
      exportLoading: false,
    }
  },
  components: {
    IncidentCombobox,
    IncidentTypeCombobox,
    IncidentPriorityCombobox,
    ProjectCombobox,
    TaskStatusMultiSelect,
    IncidentStatus,
    IncidentPriority,
    Participant,
  },
  computed: {
    ...mapFields("task", [
      "table.options.filters.incident_type",
      "table.options.filters.incident_priority",
      "table.options.filters.project",
      "table.options.filters.status",
      "table.options.filters.tag",
      "table.options.filters.incident",
      "table.options",
      "table.rows.items",
      "table.rows.total",
      "dialogs.showExport",
    ]),
  },

  methods: {
    ...mapActions("task", ["getAll", "closeExport"]),

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
      return TaskApi.getAll(params)
        .then((response) => {
          let items = response.data.items
          Util.exportCSV(items, "incident-tasks-export.csv")
          this.exportLoading = false
          this.closeExport()
        })
        .catch((err) => {
          console.log(err)
          this.exportLoading = false
          this.closeExport()
        })
    },
  },
  mounted() {
    this.$watch(
      (vm) => [vm.incident, vm.incident_type, vm.incident_priority, vm.project, vm.status],
      () => {
        this.getPreviewData()
      }
    )
  },
}
</script>
