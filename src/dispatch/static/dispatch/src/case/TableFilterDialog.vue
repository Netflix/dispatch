<template>
  <v-dialog v-model="display" max-width="600px">
    <template v-slot:activator="{ on }">
      <v-badge :value="numFilters" bordered overlap color="info" :content="numFilters">
        <v-btn color="secondary" outlined v-on="on">
          <v-icon left> mdi-filter </v-icon>
          Filter
        </v-btn>
      </v-badge>
    </template>
    <v-card>
      <v-card-title>
        <span class="headline">Case Filters</span>
      </v-card-title>
      <v-list dense>
        <v-list-item>
          <v-list-item-content>
            <date-window-input v-model="local_reported_at" label="Reported At" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <date-window-input v-model="local_closed_at" label="Closed At" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <project-combobox v-model="local_project" label="Projects" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <case-type-combobox v-model="local_case_type" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <case-severity-combobox v-model="local_case_severity" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <case-priority-combobox v-model="local_case_priority" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <case-status-multi-select v-model="local_status" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <tag-type-filter-combobox v-model="local_tag_type" label="Tag Types" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <tag-filter-auto-complete v-model="local_tag" label="Tags" />
          </v-list-item-content>
        </v-list-item>
      </v-list>
      <v-card-actions>
        <v-spacer />
        <v-btn color="info" text @click="applyFilters()"> Apply Filters </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { sum } from "lodash"
import { mapFields } from "vuex-map-fields"

import CasePriorityCombobox from "@/case/priority/CasePriorityCombobox.vue"
import CaseSeverityCombobox from "@/case/severity/CaseSeverityCombobox.vue"
import CaseStatusMultiSelect from "@/case/CaseStatusMultiSelect.vue"
import CaseTypeCombobox from "@/case/type/CaseTypeCombobox.vue"
import DateWindowInput from "@/components/DateWindowInput.vue"
import ProjectCombobox from "@/project/ProjectCombobox.vue"
import TagFilterAutoComplete from "@/tag/TagFilterAutoComplete.vue"
import TagTypeFilterCombobox from "@/tag_type/TagTypeFilterCombobox.vue"

export default {
  name: "CaseTableFilterDialog",

  components: {
    CasePriorityCombobox,
    CaseSeverityCombobox,
    CaseStatusMultiSelect,
    CaseTypeCombobox,
    DateWindowInput,
    ProjectCombobox,
    TagFilterAutoComplete,
    TagTypeFilterCombobox,
  },

  props: {
    projects: {
      type: Array,
      default: function () {
        return []
      },
    },
  },

  data() {
    return {
      display: false,
      local_case_priority: [],
      local_case_severity: [],
      local_case_type: [],
      local_closed_at: {},
      local_project: this.projects,
      local_reported_at: {},
      local_status: [],
      local_tag: [],
      local_tag_type: [],
    }
  },

  computed: {
    ...mapFields("case_management", [
      "table.options.filters.case_priority",
      "table.options.filters.case_severity",
      "table.options.filters.case_type",
      "table.options.filters.closed_at",
      "table.options.filters.project",
      "table.options.filters.reported_at",
      "table.options.filters.status",
      "table.options.filters.tag",
      "table.options.filters.tag_type",
    ]),
    numFilters: function () {
      return sum([
        this.case_priority.length,
        this.case_severity.length,
        this.case_type.length,
        this.project.length,
        this.status.length,
        this.tag.length,
        this.tag_type.length,
      ])
    },
  },

  methods: {
    applyFilters() {
      // we set the filter values
      this.case_priority = this.local_case_priority
      this.case_severity = this.local_case_severity
      this.case_type = this.local_case_type
      this.closed_at = this.local_closed_at
      this.project = this.local_project
      this.reported_at = this.local_reported_at
      this.status = this.local_status
      this.tag = this.local_tag
      this.tag_type = this.local_tag_type

      // we close the dialog
      this.display = false
    },
  },
}
</script>
