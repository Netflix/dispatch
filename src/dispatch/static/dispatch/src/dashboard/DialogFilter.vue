<template>
  <v-dialog v-model="display" max-width="600px">
    <template v-slot:activator="{ on }">
      <v-badge :value="numFilters" bordered overlap color="info" :content="numFilters">
        <v-btn color="secondary" v-on="on"> Filter </v-btn>
      </v-badge>
    </template>
    <v-card>
      <v-card-title>
        <span class="headline">Filters</span>
      </v-card-title>
      <v-list dense>
        <v-list-item>
          <v-list-item-content>
            <v-menu
              ref="menu"
              v-model="menu"
              :close-on-content-click="false"
              transition="scale-transition"
              offset-y
              min-width="290px"
            >
              <template v-slot:activator="{ on }">
                <v-text-field v-model="dateRangeText" label="Window" readonly v-on="on" />
              </template>
              <v-date-picker v-model="localWindow" type="month" range />
            </v-menu>
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <project-combobox v-model="localProject" label="Projects" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <tag-filter-combobox v-model="localTag" label="Tags" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <incident-type-combobox v-model="localIncidentType" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <incident-priority-combobox v-model="localIncidentPriority" />
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-card>
  </v-dialog>
</template>

<script>
import { parseISO } from "date-fns"
import subMonths from "date-fns/subMonths"
import { map, sum, forEach, each, has, assign } from "lodash"

import SearchUtils from "@/search/utils"
import IncidentApi from "@/incident/api"
import TagFilterCombobox from "@/tag/TagFilterCombobox.vue"
import ProjectCombobox from "@/project/ProjectCombobox.vue"
import IncidentTypeCombobox from "@/incident_type/IncidentTypeCombobox.vue"
import IncidentPriorityCombobox from "@/incident_priority/IncidentPriorityCombobox.vue"

export default {
  name: "IncidentOverviewFilterBar",

  props: {
    tag: {
      type: [String, Array],
      default: function () {
        return []
      },
    },
    incidentType: {
      type: [String, Array],
      default: function () {
        return []
      },
    },
    incidentPriority: {
      type: [String, Array],
      default: function () {
        return []
      },
    },
    project: {
      type: [String, Array],
      default: function () {
        return []
      },
    },
    window: {
      type: Array,
      default: function () {
        let now = new Date()
        let today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
        let start = subMonths(today, 6).toISOString().substr(0, 10)
        let end = today.toISOString().substr(0, 10)
        return [start, end]
      },
    },
  },

  methods: {
    fetchData() {
      let localWindow = this.localWindow
      // ensure we have a decent date string
      localWindow = map(localWindow, function (item) {
        return parseISO(item).toISOString()
      })

      if (localWindow.length == 1) {
        localWindow[1] = localWindow[0]
      }

      let filterOptions = {
        itemsPerPage: -1,
        descending: [false],
        sortBy: ["reported_at"],
        filters: {
          project: this.localProject,
          incident_type: this.localIncidentType,
          incident_priority: this.localIncidentPriority,
          tag: this.localTag,
        },
      }

      let windowFilter = [
        {
          field: "reported_at",
          op: ">=",
          value: localWindow[0],
        },
        {
          field: "reported_at",
          op: "<=",
          value: localWindow[1],
        },
      ]

      filterOptions = SearchUtils.createParametersFromTableOptions(filterOptions, windowFilter)

      this.$emit("loading", "error")
      this.$emit("filterOptions", filterOptions)
      IncidentApi.getAll(filterOptions).then((response) => {
        this.$emit("update", response.data.items)
        this.$emit("loading", false)
      })
    },
    serializeFilters() {
      let flatFilters = {}
      forEach(this.filters, function (value, key) {
        each(value, function (item) {
          if (has(flatFilters, key)) {
            flatFilters[key].push(item.name)
          } else {
            flatFilters[key] = [item.name]
          }
        })
      })
      return flatFilters
    },
    serializeWindow() {
      return { start: this.localWindow[0], end: this.localWindow[1] }
    },
    updateURL() {
      let queryParams = {}
      assign(queryParams, this.serializeFilters())
      assign(queryParams, this.serializeWindow())
      this.$router.replace({ query: queryParams })
    },
  },

  components: {
    TagFilterCombobox,
    IncidentTypeCombobox,
    IncidentPriorityCombobox,
    ProjectCombobox,
  },

  data() {
    return {
      menu: false,
      display: false,
      localWindow: this.window,
      localTag: typeof this.tag === "string" ? [{ name: this.tag }] : this.tag,
      localIncidentPriority:
        typeof this.incidentPriority === "string"
          ? [{ name: this.incidentPriority }]
          : this.incidentPriority,
      localIncidentType:
        typeof this.incidentType === "string" ? [{ name: this.incidentType }] : this.incidentType,
      localProject: typeof this.project === "string" ? [{ name: this.project }] : this.project,
    }
  },

  mounted() {
    this.$watch(
      (vm) => [
        vm.localWindow,
        vm.localTag,
        vm.localIncidentPriority,
        vm.localIncidentType,
        vm.localProject,
      ],
      () => {
        this.updateURL()
        this.fetchData()
      }
    )
  },

  created() {
    this.fetchData()
  },

  computed: {
    filters() {
      return {
        tag: this.localTag,
        incident_priority: this.localIncidentPriority,
        incident_type: this.localIncidentType,
        project: this.localProject,
      }
    },
    numFilters: function () {
      return sum([
        this.localIncidentType.length,
        this.localIncidentPriority.length,
        this.localTag.length,
        this.localProject.length,
        1,
      ])
    },
    dateRangeText() {
      return this.localWindow.join(" ~ ")
    },
  },
}
</script>
