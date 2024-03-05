<template>
  <v-dialog v-model="showExport" persistent max-width="800px">
    <template #activator="{ props }">
      <v-btn color="secondary" class="ml-2" v-bind="props"> Export </v-btn>
    </template>
    <v-card>
      <v-card-title>
        <span class="text-h5">Export Tasks</span>
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
                  <incident-combobox v-model="incident" />
                </v-list-item>
                <v-list-item>
                  <project-combobox v-model="project" label="Projects" />
                </v-list-item>
                <v-list-item>
                  <task-status-multi-select v-model="status" />
                </v-list-item>
                <v-list-item>
                  <incident-type-combobox v-model="incident_type" label="Incident Type" />
                </v-list-item>
                <v-list-item>
                  <incident-priority-combobox
                    v-model="incident_priority"
                    label="Incident Priority"
                  />
                </v-list-item>
              </v-list>
              <v-btn color="info" @click="e1 = 2"> Continue </v-btn>

              <v-btn @click="closeExport()" variant="text"> Cancel </v-btn>
            </div>
          </v-stepper-window-item>

          <v-stepper-window-item :value="2">
            <div class="scrollable-container">
              <v-autocomplete
                v-model="selectedFields"
                :items="allFields"
                label="Fields"
                multiple
                chips
                return-object
              />
              <v-btn color="info" @click="e1 = 3"> Continue </v-btn>

              <v-btn @click="closeExport()" variant="text"> Cancel </v-btn>
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
                <template #item.description="{ item }">
                  <div class="text-truncate" style="max-width: 400px">
                    {{ item.description }}
                  </div>
                </template>
                <template #item.incident.status="{ item }">
                  <incident-status :status="item.incident.status" :id="item.id" />
                </template>
                <template #item.incident_priority.name="{ item }">
                  <incident-priority :priority="item.incident.incident_priority.name" />
                </template>
                <template #item.creator.individual_contact.name="{ item }">
                  <participant :participant="item.creator" />
                </template>
                <template #item.owner.individual_contact.name="{ item }">
                  <participant :participant="item.owner" />
                </template>
                <template #item.incident_type.name="{ item }">
                  {{ item.incident.incident_type.name }}
                </template>
                <template #item.assignees="{ item }">
                  <participant
                    v-for="assignee in item.assignees"
                    :key="assignee.id"
                    :participant="assignee"
                  />
                </template>
                <template #item.resolve_by="{ item }">
                  {{ formatDate(item.resolve_by) }}
                </template>
                <template #item.created_at="{ item }">
                  {{ formatDate(item.created_at) }}
                </template>
                <template #item.resolved_at="{ item }">
                  {{ formatDate(item.resolved_at) }}
                </template>
                <template #item.source="{ item }">
                  {{ item.source }}
                  <a :href="item.weblink" target="_blank" style="text-decoration: none" />
                </template>
              </v-data-table>
              <v-badge :model-value="!!total" color="info" bordered :content="total">
                <v-btn color="info" @click="exportToCSV()" :loading="exportLoading"> Export </v-btn>
              </v-badge>

              <v-btn @click="closeExport()" variant="text"> Cancel </v-btn>
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
import { formatDate } from "@/filters"
import Util from "@/util"
import SearchUtils from "@/search/utils"

import IncidentCombobox from "@/incident/IncidentFilterCombobox.vue"
import IncidentPriority from "@/incident/priority/IncidentPriority.vue"
import IncidentPriorityCombobox from "@/incident/priority/IncidentPriorityCombobox.vue"
import IncidentStatus from "@/incident/status/IncidentStatus.vue"
import IncidentTypeCombobox from "@/incident/type/IncidentTypeCombobox.vue"
import Participant from "@/incident/Participant.vue"
import ProjectCombobox from "@/project/ProjectCombobox.vue"
import TaskApi from "@/task/api"
import TaskStatusMultiSelect from "@/task/TaskStatusMultiSelect.vue"

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
        { text: "Due By", value: "resolve_by", sortable: true },
        { text: "Created At", value: "created_at", sortable: true },
        { text: "Resolved At", value: "resolved_at", sortable: true },
      ],
      previewRowsLoading: false,
      exportLoading: false,
    }
  },
  setup() {
    return { formatDate }
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
  created() {
    this.$watch(
      (vm) => [vm.incident, vm.incident_type, vm.incident_priority, vm.project, vm.status],
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
