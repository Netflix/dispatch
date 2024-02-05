<template>
  <v-dialog v-model="display" max-width="600px">
    <template #activator="{ props }">
      <v-badge :model-value="!!numFilters" bordered color="info" :content="numFilters">
        <v-btn color="secondary" v-bind="props"> Filter </v-btn>
      </v-badge>
    </template>
    <v-card>
      <v-card-title>
        <span class="text-h5">Dashboard Case Filters</span>
      </v-card-title>
      <v-list density="compact">
        <v-list-item>
          <date-window-input v-model="filters.reported_at" label="Reported At" />
        </v-list-item>
        <v-list-item>
          <date-window-input v-model="filters.closed_at" label="Closed At" />
        </v-list-item>
        <v-list-item>
          <project-combobox v-model="filters.project" label="Projects" />
        </v-list-item>
        <v-list-item>
          <tag-filter-auto-complete
            v-model="filters.tag"
            label="Tags"
            model="case"
            :project="filters.project"
          />
        </v-list-item>
        <v-list-item>
          <case-type-combobox v-model="filters.case_type" />
        </v-list-item>
        <v-list-item>
          <case-severity-combobox v-model="filters.case_severity" />
        </v-list-item>
        <v-list-item>
          <case-priority-combobox v-model="filters.case_priority" />
        </v-list-item>
      </v-list>
      <v-card-actions>
        <v-spacer />
        <v-btn color="info" variant="text" @click="applyFilters()"> Apply Filters </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { sum } from "lodash"

import startOfMonth from "date-fns/startOfMonth"
import subMonths from "date-fns/subMonths"

import CaseApi from "@/case/api"
import CasePriorityCombobox from "@/case/priority/CasePriorityCombobox.vue"
import CaseSeverityCombobox from "@/case/severity/CaseSeverityCombobox.vue"
import CaseTypeCombobox from "@/case/type/CaseTypeCombobox.vue"
import DateWindowInput from "@/components/DateWindowInput.vue"
import ProjectCombobox from "@/project/ProjectCombobox.vue"
import RouterUtils from "@/router/utils"
import SearchUtils from "@/search/utils"
import TagFilterAutoComplete from "@/tag/TagPicker.vue"

let today = function () {
  let now = new Date()
  return new Date(now.getFullYear(), now.getMonth(), now.getDate())
}

export default {
  name: "CaseOverviewFilterDialog",

  components: {
    CasePriorityCombobox,
    CaseSeverityCombobox,
    CaseTypeCombobox,
    DateWindowInput,
    ProjectCombobox,
    TagFilterAutoComplete,
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
      menuStart: false,
      menuEnd: false,
      display: false,
      filters: {
        case_priority: [],
        case_severity: [],
        case_type: [],
        project: this.projects,
        status: [],
        tag: [],
        reported_at: {
          start: null,
          end: null,
        },
        closed_at: {
          start: null,
          end: null,
        },
      },
    }
  },

  computed: {
    numFilters: function () {
      return sum([
        this.filters.case_priority.length,
        this.filters.case_severity.length,
        this.filters.case_type.length,
        this.filters.project.length,
        this.filters.status.length,
        this.filters.tag.length,
        1,
      ])
    },
  },

  methods: {
    applyFilters() {
      RouterUtils.updateURLFilters(this.filters)
      this.fetchData()
      // we close the dialog
      this.display = false
    },
    fetchData() {
      let filterOptions = {
        itemsPerPage: -1,
        descending: [false],
        sortBy: ["reported_at"],
        filters: { ...this.filters },
        include: [
          "case_priority",
          "case_severity",
          "case_type",
          "closed_at",
          "duplicates",
          "escalated_at",
          "incidents",
          "name",
          "project",
          "reported_at",
          "status",
          "tags",
          "title",
          "triage_at",
        ],
      }

      this.$emit("loading", "error")
      filterOptions = SearchUtils.createParametersFromTableOptions(filterOptions)
      CaseApi.getAll(filterOptions).then((response) => {
        this.$emit("update", response.data.items)
        this.$emit("loading", false)
      })
    },
  },

  created() {
    this.filters = {
      ...this.filters,
      ...{
        reported_at: {
          start: startOfMonth(subMonths(today(), 1)).toISOString().slice(0, -1),
          end: today().toISOString().slice(0, -1),
        },
      },
      ...RouterUtils.deserializeFilters(this.$route.query), // Order matters as values will overwrite
    }
    this.fetchData()
  },
}
</script>
