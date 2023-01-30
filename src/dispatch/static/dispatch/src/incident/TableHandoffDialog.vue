<template>
  <v-dialog v-model="showHandoff" persistent max-width="800px">
    <template v-slot:activator="{ on }">
      <v-btn color="secondary" class="ml-2" v-on="on"> Handoff </v-btn>
    </template>
    <v-card>
      <v-card-title>
        <span class="headline">Handoff Incidents</span>
      </v-card-title>
      <v-stepper v-model="e1">
        <v-stepper-header>
          <v-stepper-step :complete="e1 > 1" step="1" editable> Filter Incidents </v-stepper-step>
          <v-divider />
          <v-stepper-step :complete="e1 > 2" step="2" editable> Preview Incidents </v-stepper-step>
          <v-divider />
          <v-stepper-step step="3" editable> Select Commander </v-stepper-step>
        </v-stepper-header>
        <v-stepper-items>
          <v-stepper-content step="1">
            <v-list dense>
              <v-list-item>
                <v-list-item-content>
                  <date-window-input v-model="reported_at" label="Reported At" />
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <project-combobox v-model="project" label="Projects" />
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <incident-status-multi-select v-model="status" />
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <incident-type-combobox v-model="incident_type" />
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <incident-severity-combobox v-model="incident_severity" />
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <incident-priority-combobox v-model="incident_priority" />
                </v-list-item-content>
              </v-list-item>
            </v-list>
            <v-spacer />
            <v-btn @click="closeHandoff()" text> Cancel </v-btn>
            <v-btn color="info" @click="e1 = 2"> Continue </v-btn>
          </v-stepper-content>
          <v-stepper-content step="2">
            <v-data-table
              hide-default-footer
              :headers="selectedFields"
              :items="items"
              :loading="previewRowsLoading"
            >
              <template v-slot:item.incident_severity.name="{ item }">
                <incident-severity :severity="item.incident_severity.name" />
              </template>
              <template v-slot:item.incident_priority.name="{ item }">
                <incident-priority :priority="item.incident_priority.name" />
              </template>
              <template v-slot:item.status="{ item }">
                <incident-status :status="item.status" :id="item.id" />
              </template>
            </v-data-table>
            <v-spacer />
            <v-btn @click="closeHandoff()" text> Cancel </v-btn>
            <v-btn color="info" @click="e1 = 3"> Continue </v-btn>
          </v-stepper-content>
          <v-stepper-content step="3">
            <v-flex xs12>
              <participant-select label="Commander" :project="project"/>
            </v-flex>
            <!-- <v-list dense> -->
            <!--   <v-list-item> -->
            <!--     <v-list-item-content> -->
            <!--     </v-list-item-content> -->
            <!--   </v-list-item> -->
            <!-- </v-list> -->
            <v-spacer />
            <v-btn @click="closeHandoff()" text> Cancel </v-btn>
            <v-badge :value="total" overlap color="info" bordered :content="total">
              <v-btn color="info" @click="handoffIncidents()" :loading="handoffLoading"> Handoff </v-btn>
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

import DateWindowInput from "@/components/DateWindowInput.vue"
import IncidentApi from "@/incident/api"
import IncidentPriority from "@/incident/priority/IncidentPriority.vue"
import IncidentPriorityCombobox from "@/incident/priority/IncidentPriorityCombobox.vue"
import IncidentSeverity from "@/incident/severity/IncidentSeverity.vue"
import IncidentSeverityCombobox from "@/incident/severity/IncidentSeverityCombobox.vue"
import IncidentStatus from "@/incident/status/IncidentStatus.vue"
import IncidentStatusMultiSelect from "@/incident/status/IncidentStatusMultiSelect.vue"
import IncidentTypeCombobox from "@/incident/type/IncidentTypeCombobox.vue"
import ParticipantSelect from "@/incident/ParticipantSelect.vue"
import ProjectCombobox from "@/project/ProjectCombobox.vue"
import TagFilterAutoComplete from "@/tag/TagFilterAutoComplete.vue"
import TagTypeFilterCombobox from "@/tag_type/TagTypeFilterCombobox.vue"

export default {
  name: "IncidentTableHandoffDialog",

  components: {
    DateWindowInput,
    IncidentPriority,
    IncidentPriorityCombobox,
    IncidentSeverity,
    IncidentSeverityCombobox,
    IncidentStatus,
    IncidentStatusMultiSelect,
    IncidentTypeCombobox,
    ParticipantSelect,
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
        { text: "Status", value: "status", sortable: false },
        { text: "Incident Type", value: "incident_type.name", sortable: false },
        { text: "Incident Severity", value: "incident_severity.name", sortable: false },
      ],
      previewRowsLoading: false,
      handoffLoading: false,
    }
  },

  computed: {
    ...mapFields("incident", [
      "dialogs.showHandoff",
      "table.options",
      "table.options.filters.incident_priority",
      "table.options.filters.incident_severity",
      "table.options.filters.incident_type",
      "table.options.filters.project",
      "table.options.filters.reported_at",
      "table.options.filters.status",
      "table.rows.items",
      "table.rows.total",
    ]),
  },

  methods: {
    ...mapActions("incident", ["getAll", "closeHandoff"]),

    getPreviewData() {
      this.previewRowsLoading = "error"
      this.getAll({ itemsPerPage: 10 })
      this.previewRowsLoading = false
    },

    handoffIncidents() {
      let params = SearchUtils.createParametersFromTableOptions({ ...this.options })

      params["itemsPerPage"] = -1
      params["include"] = this.selectedFields.map((item) => item.value)

      this.handoffLoading = true

      return IncidentApi.handoff(params)
        .then((response) => {
          <!-- let items = response.data.items -->
          this.handoffLoading = false
          this.closeHandoff()
        })
        .catch((error) => {
          console.log(error)
          this.handoffLoading = false
          this.closeHandoff()
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
