<template>
  <v-dialog v-model="showCreate" persistent max-width="800px">
    <template #activator="{ props }">
      <v-btn icon variant="text" v-bind="props">
        <v-icon>mdi-plus</v-icon>
      </v-btn>
    </template>
    <v-card>
      <v-card-title class="d-flex">
        <span class="text-h5">Create Search Filter</span>
        <v-spacer />
        <v-radio-group v-model="subject" class="flex-0-0" inline>
          <v-radio label="Incident" value="incident" />
          <v-radio label="Case" value="case" />
        </v-radio-group>
      </v-card-title>
      <v-stepper v-model="step">
        <v-stepper-header>
          <v-stepper-item :complete="step > 1" :value="1" editable> Filter </v-stepper-item>
          <v-divider />

          <v-stepper-item :complete="step > 2" :value="2" editable> Preview </v-stepper-item>
          <v-divider />

          <v-stepper-item :value="3" editable> Save </v-stepper-item>
        </v-stepper-header>

        <v-stepper-window>
          <v-stepper-window-item :value="1">
            <v-card>
              <v-card-text>
                <v-tabs v-model="activeTab" color="primary" align-tabs="end">
                  <v-tab>Basic</v-tab>
                  <v-tab>Advanced</v-tab>
                </v-tabs>
                <v-window v-model="activeTab">
                  <v-window-item>
                    <v-list v-if="subject == 'incident'" density="compact">
                      <v-list-item>
                        <tag-filter-auto-complete
                          :project="project"
                          v-model="filters.tag"
                          label="Tags"
                          model="incident"
                        />
                      </v-list-item>
                      <v-list-item>
                        <tag-type-filter-combobox
                          :project="project"
                          v-model="filters.tag_type"
                          label="Tag Types"
                        />
                      </v-list-item>
                      <v-list-item>
                        <incident-type-combobox
                          :project="project"
                          v-model="filters.incident_type"
                        />
                      </v-list-item>
                      <v-list-item>
                        <incident-priority-combobox
                          :project="project"
                          v-model="filters.incident_priority"
                        />
                      </v-list-item>
                      <v-list-item>
                        <incident-status-multi-select v-model="filters.status" />
                      </v-list-item>
                      <v-list-item>
                        <v-select
                          :items="visibilities"
                          v-model="filters.visibility"
                          name="visibility"
                          item-title="name"
                          return-object
                          label="Visibility"
                        />
                      </v-list-item>
                    </v-list>
                    <v-list v-else>
                      <v-list-item>
                        <tag-filter-auto-complete
                          :project="project"
                          v-model="filters.tag"
                          label="Tags"
                        />
                      </v-list-item>
                      <v-list-item>
                        <tag-type-filter-combobox
                          :project="project"
                          v-model="filters.tag_type"
                          label="Tag Types"
                        />
                      </v-list-item>
                      <v-list-item>
                        <case-type-combobox :project="project" v-model="filters.case_type" />
                      </v-list-item>
                      <v-list-item>
                        <case-priority-combobox
                          :project="project"
                          v-model="filters.case_priority"
                        />
                      </v-list-item>
                      <v-list-item>
                        <incident-status-multi-select v-model="filters.status" />
                      </v-list-item>
                      <v-list-item>
                        <v-select
                          :items="visibilities"
                          v-model="filters.visibility"
                          name="visibility"
                          item-title="name"
                          return-object
                          label="Visibility"
                        />
                      </v-list-item>
                    </v-list>
                  </v-window-item>
                  <v-window-item>
                    <div style="height: 400px">
                      <MonacoEditor
                        v-model="expression_str"
                        :options="editorOptions"
                        language="json"
                      />
                    </div>
                  </v-window-item>
                </v-window>
              </v-card-text>
              <v-card-actions>
                <v-spacer />
                <v-btn @click="closeCreateDialog()" variant="text"> Cancel </v-btn>
                <v-btn color="info" @click="step = 2"> Continue </v-btn>
              </v-card-actions>
            </v-card>
          </v-stepper-window-item>

          <v-stepper-window-item :value="2">
            <v-card>
              <v-card-text>
                Examples matching your filter:
                <v-data-table
                  hide-default-footer
                  :headers="previewFields"
                  :items="previewRows.items"
                  :loading="previewRowsLoading"
                >
                  <template #item.incident_priority.name="{ item }">
                    <incident-priority :priority="item.incident_priority.name" />
                  </template>
                  <template #item.status="{ item }">
                    <incident-status :status="item.status" :id="item.id" />
                  </template>
                </v-data-table>
              </v-card-text>
              <v-card-actions>
                <v-spacer />
                <v-btn @click="closeCreateDialog()" variant="text"> Cancel </v-btn>
                <v-btn color="info" @click="step = 3" :loading="loading"> Continue </v-btn>
              </v-card-actions>
            </v-card>
          </v-stepper-window-item>
          <v-stepper-window-item :value="3">
            <v-form @submit.prevent v-slot="{ isValid }">
              <v-card>
                <v-card-text>
                  Provide a name and description for your filter.
                  <v-text-field
                    v-model="name"
                    label="Name"
                    hint="A name for your saved search."
                    clearable
                    required
                    name="Name"
                    :rules="[rules.required]"
                  />
                  <v-textarea
                    v-model="description"
                    label="Description"
                    hint="A short description."
                    clearable
                    auto-grow
                    required
                    name="Description"
                    :rules="[rules.required]"
                  />
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn @click="closeCreateDialog()" variant="text"> Cancel </v-btn>
                  <v-btn
                    color="info"
                    @click="saveFilter()"
                    :loading="loading"
                    :disabled="!isValid.value"
                  >
                    Save
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-form>
          </v-stepper-window-item>
        </v-stepper-window>
      </v-stepper>
    </v-card>
  </v-dialog>
</template>

<script>
import MonacoEditor from "@/components/MonacoEditor.vue"

import { required } from "@/util/form"

import { mapActions } from "vuex"
import { mapFields } from "vuex-map-fields"

import CaseApi from "@/case/api"
import CasePriorityCombobox from "@/case/priority/CasePriorityCombobox.vue"
import CaseTypeCombobox from "@/case/type/CaseTypeCombobox.vue"
import IncidentApi from "@/incident/api"
import IncidentPriority from "@/incident/priority/IncidentPriority.vue"
import IncidentPriorityCombobox from "@/incident/priority/IncidentPriorityCombobox.vue"
import IncidentStatus from "@/incident/status/IncidentStatus.vue"
import IncidentStatusMultiSelect from "@/incident/status/IncidentStatusMultiSelect.vue"
import IncidentTypeCombobox from "@/incident/type/IncidentTypeCombobox.vue"
import SearchUtils from "@/search/utils"
import TagFilterAutoComplete from "@/tag/TagPicker.vue"
import TagTypeFilterCombobox from "@/tag_type/TagTypeFilterCombobox.vue"

export default {
  setup() {
    return {
      rules: { required },
    }
  },
  name: "SearchFilterCreateDialog",
  data() {
    return {
      visibilities: [{ name: "Open" }, { name: "Restricted" }],
      editorOptions: {
        automaticLayout: true,
        renderValidationDecorations: "on",
      },
      previewFields: [],
      incidentPreviewFields: [
        { text: "Name", value: "name", sortable: false },
        { text: "Title", value: "title", sortable: false },
        { text: "Status", value: "status", sortable: false },
        { text: "Incident Type", value: "incident_type.name", sortable: false },
        { text: "Incident Priority", value: "incident_priority.name", sortable: false },
      ],
      casePreviewFields: [
        { text: "Name", value: "name", sortable: false },
        { text: "Title", value: "title", sortable: false },
        { text: "Status", value: "status", sortable: false },
        { text: "Case Type", value: "case_type.name", sortable: false },
        { text: "Case Priority", value: "case_priority.name", sortable: false },
      ],
      activeTab: 0,
      step: 1,
      previewRows: {
        items: [],
        total: null,
      },
      previewRowsLoading: false,
      filters: {
        incident_type: [],
        incident_priority: [],
        case_type: [],
        case_priority: [],
        status: [],
        tag: [],
        project: [],
        tag_type: [],
        visibility: [],
      },
    }
  },
  components: {
    CasePriorityCombobox,
    CaseTypeCombobox,
    IncidentPriority,
    IncidentPriorityCombobox,
    IncidentStatus,
    IncidentStatusMultiSelect,
    IncidentTypeCombobox,
    TagFilterAutoComplete,
    TagTypeFilterCombobox,
    MonacoEditor,
  },
  computed: {
    ...mapFields("search", [
      "selected",
      "selected.description",
      "selected.expression",
      "selected.subject",
      "selected.name",
      "selected.project",
      "loading",
      "dialogs.showCreate",
    ]),
    expression_str: {
      get: function () {
        return JSON.stringify(this.expression, null, "\t") || "[]"
      },
      set: function (newValue) {
        this.expression = JSON.parse(newValue)
      },
    },
  },
  methods: {
    ...mapActions("search", ["closeCreateDialog", "save"]),
    saveFilter() {
      // reset local data
      this.save("incident").then((filter) => {
        this.$emit("save", filter)
      })
    },
    resetFilters() {
      this.filters = {
        incident_type: [],
        incident_priority: [],
        case_type: [],
        case_priority: [],
        status: [],
        tag: [],
        project: [],
        tag_type: [],
        visibility: [],
      }
    },
    getPreviewData() {
      let params = {}
      if (this.expression) {
        params = { filter: JSON.stringify(this.expression) }
        this.previewRowsLoading = "error"
      }
      if (this.subject === "incident") {
        return IncidentApi.getAll(params).then((response) => {
          this.previewFields = this.incidentPreviewFields
          this.previewRows = response.data
          this.previewRowsLoading = false
        })
      } else {
        return CaseApi.getAll(params).then((response) => {
          this.previewFields = this.casePreviewFields
          this.previewRows = response.data
          this.previewRowsLoading = false
        })
      }
    },
  },
  created() {
    if (this.$route.query.project) {
      this.project = { name: this.$route.query.project }
    }
    this.getPreviewData()
    this.$watch(
      (vm) => [vm.subject],
      () => {
        this.resetFilters()
      }
    )

    this.$watch(
      (vm) => [
        vm.filters.incident_type,
        vm.filters.incident_priority,
        vm.filters.case_priority,
        vm.filters.case_type,
        vm.filters.status,
        vm.filters.tag,
        vm.filters.tag_type,
        vm.filters.visibility,
      ],
      () => {
        if (this.subject === "incident") {
          this.expression = SearchUtils.createFilterExpression(this.filters, "Incident")
        } else {
          this.expression = SearchUtils.createFilterExpression(this.filters, "Case")
        }
        this.getPreviewData()
      }
    )
  },
}
</script>
