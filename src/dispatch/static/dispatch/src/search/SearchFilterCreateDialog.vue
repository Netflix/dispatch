<template>
  <v-dialog v-model="showCreate" persistent max-width="800px">
    <template v-slot:activator="{ on }">
      <v-btn color="secondary" class="ml-2" v-on="on">Create</v-btn>
    </template>
    <v-card>
      <v-card-title>
        <span class="headline">Create Search Filter</span>
      </v-card-title>
      <v-stepper v-model="e1">
        <v-stepper-header>
          <v-stepper-step :complete="e1 > 1" step="1" editable>
            Filter
          </v-stepper-step>
          <v-divider></v-divider>

          <v-stepper-step step="2" editable>
            Preview
          </v-stepper-step>
        </v-stepper-header>

        <v-stepper-items>
          <v-stepper-content step="1">
            <v-tabs color="primary" right>
              <v-tab>Basic</v-tab>
              <v-tab>Advanced</v-tab>
              <v-tab-item>
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
              </v-tab-item>
              <v-tab-item>
                <div style="height: 400px">
                  <advanced-editor v-model="expression"></advanced-editor>
                </div>
              </v-tab-item>
            </v-tabs>

            <v-btn color="info" @click="e1 = 2">
              Continue
            </v-btn>

            <v-btn @click="closeCreateDialog()" text>
              Cancel
            </v-btn>
          </v-stepper-content>

          <v-stepper-content step="2">
            <v-data-table
              hide-default-footer
              :headers="previewFields"
              :items="previewRows.items"
              :loading="previewRowsLoading"
            >
              <template v-slot:item.incident_priority.name="{ item }">
                <incident-priority :priority="item.incident_priority.name" />
              </template>
              <template v-slot:item.status="{ item }">
                <incident-status :status="item.status" :id="item.id" />
              </template>
            </v-data-table>
            <v-textarea
              v-model="description"
              label="Description"
              hint="A short description."
              clearable
              auto-grow
            />
            <v-btn color="info" @click="save()" :loading="loading">
              Save
            </v-btn>
            <v-btn @click="closeCreateDialog()" text>
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
import IncidentStatus from "@/incident/IncidentStatus.vue"
import IncidentPriority from "@/incident/IncidentPriority.vue"
import AdvancedEditor from "@/search/AdvancedEditor.vue"

const toPascalCase = str =>
  `${str}`
    .replace(new RegExp(/[-_]+/, "g"), " ")
    .replace(new RegExp(/[^\w\s]/, "g"), "")
    .replace(
      new RegExp(/\s+(.)(\w+)/, "g"),
      ($1, $2, $3) => `${$2.toUpperCase() + $3.toLowerCase()}`
    )
    .replace(new RegExp(/\s/, "g"), "")
    .replace(new RegExp(/\w/), s => s.toUpperCase())

export default {
  name: "SearchFilterCreateDialog",
  data() {
    return {
      e1: 1,
      previewFields: [
        { text: "Name", value: "name", sortable: false },
        { text: "Title", value: "title", sortable: false },
        { text: "Status", value: "status", sortable: false },
        { text: "Incident Type", value: "incident_type.name", sortable: false },
        { text: "Incident Priority", value: "incident_priority.name", sortable: false }
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
      filterExpression: null
    }
  },
  components: {
    TagFilterCombobox,
    IncidentTypeCombobox,
    IncidentPriorityCombobox,
    IncidentStatusMultiSelect,
    IncidentStatus,
    IncidentPriority,
    AdvancedEditor
  },
  computed: {
    ...mapFields("search", [
      "selected.description",
      "selected.expression",
      "selected.type",
      "loading",
      "dialogs.showCreate"
    ])
  },

  methods: {
    ...mapActions("search", ["closeCreateDialog", "save"]),

    createFilterExpression(filters) {
      let filterExpression = []
      forEach(filters, function(value, key) {
        each(value, function(value) {
          if (has(value, "id")) {
            filterExpression.push({
              model: toPascalCase(key),
              field: "id",
              op: "==",
              value: value.id
            })
          } else {
            filterExpression.push({ field: key, op: "==", value: value })
          }
        })
      })

      if (filterExpression.length > 0) {
        return [{ and: filterExpression }]
      } else {
        return []
      }
    },

    getPreviewData() {
      let params = { filter: JSON.stringify(this.expression) }
      this.previewRowsLoading = "error"
      return IncidentApi.getAll(params).then(response => {
        this.previewRows = response.data
        this.previewRowsLoading = false
      })
    }
  },
  mounted() {
    this.getPreviewData()
    this.$watch(
      vm => [
        vm.filters.incident_type,
        vm.filters.incident_priority,
        vm.filters.status,
        vm.filters.tag
      ],
      () => {
        this.expression = this.createFilterExpression(this.filters)
        this.getPreviewData()
      }
    )
  }
}
</script>
