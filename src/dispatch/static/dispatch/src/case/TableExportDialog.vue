<template>
  <v-dialog v-model="showExport" persistent max-width="800px">
    <template v-slot:activator="{ on }">
      <v-btn color="secondary" class="ml-2" v-on="on"> Export </v-btn>
    </template>
    <v-card>
      <v-card-title>
        <span class="headline">Export Cases</span>
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
                  <case-type-combobox v-model="case_type" />
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <case-severity-combobox v-model="case_severity" />
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <case-priority-combobox v-model="case_priority" />
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <case-status-multi-select v-model="status" />
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
              <template v-slot:item.case_severity.name="{ item }">
                <case-severity :severity="item.case_severity.name" />
              </template>
              <template v-slot:item.case_priority.name="{ item }">
                <case-priority :priority="item.case_priority.name" />
              </template>
              <template v-slot:item.status="{ item }">
                <case-status :status="item.status" :id="item.id" />
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

import CaseApi from "@/case/api"
import CasePriority from "@/case/priority/CasePriority.vue"
import CasePriorityCombobox from "@/case/priority/CasePriorityCombobox.vue"
import CaseSeverity from "@/case/severity/CaseSeverity.vue"
import CaseSeverityCombobox from "@/case/severity/CaseSeverityCombobox.vue"
import CaseStatus from "@/case/CaseStatus.vue"
import CaseStatusMultiSelect from "@/case/CaseStatusMultiSelect.vue"
import CaseTypeCombobox from "@/case/type/CaseTypeCombobox.vue"
import DateWindowInput from "@/components/DateWindowInput.vue"
import ProjectCombobox from "@/project/ProjectCombobox.vue"
import TagFilterAutoComplete from "@/tag/TagFilterAutoComplete.vue"
import TagTypeFilterCombobox from "@/tag_type/TagTypeFilterCombobox.vue"

export default {
  name: "CaseTableExportDialog",

  components: {
    CasePriority,
    CasePriorityCombobox,
    CaseSeverity,
    CaseSeverityCombobox,
    CaseStatus,
    CaseStatusMultiSelect,
    CaseTypeCombobox,
    DateWindowInput,
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
        { text: "Case Type", value: "case_type.name", sortable: false },
        { text: "Case Severity", value: "case_severity.name", sortable: false },
        { text: "Case Priority", value: "case_priority.name", sortable: false },
      ],
      allFields: [
        { text: "Reported At", value: "reported_at", sortable: false },
        { text: "Triage At", value: "triage_at", sortable: false },
        { text: "Escalated At", value: "escalated_at", sortable: false },
        { text: "Closed At", value: "closed_at", sortable: false },
        { text: "Name", value: "name", sortable: false },
        { text: "Title", value: "title", sortable: false },
        { text: "Description", value: "description", sortable: false },
        { text: "Resolution", value: "resolution", sortable: false },
        { text: "Status", value: "status", sortable: false },
        { text: "Visibility", value: "visibility", sortable: false },
        { text: "Type", value: "case_type.name", sortable: false },
        { text: "Severity", value: "case_severity.name", sortable: false },
        { text: "Priority", value: "case_priority.name", sortable: false },
        { text: "Assignee", value: "assignee.email", sortable: false },
        { text: "Document Weblink", value: "case_document.weblink", sortable: false },
        { text: "Storage Weblink", value: "storage.weblink", sortable: false },
      ],
      previewRowsLoading: false,
      exportLoading: false,
    }
  },

  computed: {
    ...mapFields("case_management", [
      "table.options",
      "table.options.filters.case_priority",
      "table.options.filters.case_severity",
      "table.options.filters.case_type",
      "table.options.filters.project",
      "table.options.filters.reported_at",
      "table.options.filters.status",
      "table.options.filters.tag",
      "table.options.filters.tag_type",
      "table.rows.items",
      "table.rows.total",
      "dialogs.showExport",
    ]),
  },

  methods: {
    ...mapActions("case_management", ["getAll", "closeExport"]),

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

      return CaseApi.getAll(params)
        .then((response) => {
          let items = response.data.items
          Util.exportCSV(items, "case-details-export.csv")
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
        vm.case_priority,
        vm.case_severity,
        vm.case_type,
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
