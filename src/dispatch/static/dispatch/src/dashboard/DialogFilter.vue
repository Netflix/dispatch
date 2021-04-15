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
            <v-col cols="12" sm="6" md="6">
              <v-menu
                v-model="menuStart"
                :close-on-content-click="false"
                transition="scale-transition"
                offset-y
                min-width="auto"
              >
                <template v-slot:activator="{ on, attrs }">
                  <v-text-field
                    v-model="filters.window.start"
                    label="Reported After"
                    prepend-icon="mdi-calendar"
                    v-bind="attrs"
                    v-on="on"
                  ></v-text-field>
                </template>
                <v-date-picker
                  v-model="filters.window.start"
                  @input="menuStart = false"
                ></v-date-picker>
              </v-menu>
            </v-col>
            <v-col cols="12" sm="6" md="6">
              <v-menu
                v-model="menuEnd"
                :close-on-content-click="false"
                transition="scale-transition"
                offset-y
                min-width="auto"
              >
                <template v-slot:activator="{ on, attrs }">
                  <v-text-field
                    v-model="filters.window.end"
                    label="Reported Before"
                    prepend-icon="mdi-calendar"
                    v-bind="attrs"
                    v-on="on"
                  ></v-text-field>
                </template>
                <v-date-picker
                  v-model="filters.window.end"
                  @input="menuEnd = false"
                ></v-date-picker>
              </v-menu>
            </v-col>
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <project-combobox v-model="filters.project" label="Projects" />
          </v-list-item-content>
        </v-list-item>
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
      </v-list>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import subMonths from "date-fns/subMonths"
import { sum } from "lodash"

import RouterUtils from "@/router/utils"
import SearchUtils from "@/search/utils"
import IncidentApi from "@/incident/api"
import TagFilterCombobox from "@/tag/TagFilterCombobox.vue"
import ProjectCombobox from "@/project/ProjectCombobox.vue"
import IncidentTypeCombobox from "@/incident_type/IncidentTypeCombobox.vue"
import IncidentPriorityCombobox from "@/incident_priority/IncidentPriorityCombobox.vue"

let defaultStart = function () {
  let now = new Date()
  let today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  return subMonths(today, 6).toISOString().substr(0, 10)
}

let defaultEnd = function () {
  let now = new Date()
  let today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  return today.toISOString().substr(0, 10)
}

export default {
  name: "IncidentOverviewFilterBar",

  data() {
    return {
      menuStart: false,
      menuEnd: false,
      display: false,
      filters: {
        project: [],
        incident_type: [],
        incident_priority: [],
        status: [],
        tag: [],
        window: {
          start: defaultStart(),
          end: defaultEnd(),
        },
      },
    }
  },

  computed: {
    numFilters: function () {
      return sum([
        this.filters.tag.length,
        this.filters.incident_priority.length,
        this.filters.incident_type.length,
        this.filters.status.length,
        this.filters.project.length,
        1,
      ])
    },
    ...mapFields("route", ["query"]),
  },

  methods: {
    fetchData() {
      let windowFilter = [
        {
          model: "Incident",
          field: "reported_at",
          op: ">=",
          value: this.filters.window.start,
        },
        {
          model: "Incident",
          field: "reported_at",
          op: "<=",
          value: this.filters.window.end,
        },
      ]

      let localFilters = { ...this.filters }
      delete localFilters.window

      let filterOptions = {
        itemsPerPage: -1,
        descending: [false],
        sortBy: ["reported_at"],
        filters: localFilters,
      }

      filterOptions = SearchUtils.createParametersFromTableOptions(filterOptions, windowFilter)

      this.$emit("loading", "error")
      this.$emit("filterOptions", filterOptions)
      IncidentApi.getAll(filterOptions).then((response) => {
        this.$emit("update", response.data.items)
        this.$emit("loading", false)
      })
    },
  },

  components: {
    TagFilterCombobox,
    IncidentTypeCombobox,
    IncidentPriorityCombobox,
    ProjectCombobox,
  },

  created() {
    this.filters = { ...this.filters, ...RouterUtils.deserializeFilters(this.query) }
    this.fetchData()
    this.$watch(
      (vm) => [
        vm.filters.window.start,
        vm.filters.window.end,
        vm.filters.tag,
        vm.filters.incident_priority,
        vm.filters.incident_type,
        vm.filters.status,
        vm.filters.project,
      ],
      () => {
        RouterUtils.updateURLFilters(this.filters)
        this.fetchData()
      }
    )
  },
}
</script>
