<template>
  <v-dialog v-model="display" max-width="600px">
    <template v-slot:activator="{ on }">
      <v-badge :value="numFilters" bordered overlap color="info" :content="numFilters">
        <v-btn color="secondary" v-on="on"> Filter </v-btn>
      </v-badge>
    </template>
    <v-card>
      <v-card-title>
        <span class="headline">Column Filters</span>
      </v-card-title>
      <v-list dense>
        <v-list-item>
          <v-list-item-content>
            <incident-combobox v-model="localIncident" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <project-combobox v-model="localProject" />
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-card>
  </v-dialog>
</template>

<script>
import { sum } from "lodash"
import SearchUtils from "@/search/utils"
import IncidentCombobox from "@/incident/IncidentCombobox.vue"
import ProjectCombobox from "@/project/ProjectCombobox.vue"
import FeedbackApi from "@/feedback/api"

export default {
  name: "FeedbackTableFilterDialog",

  props: {
    incident: {
      type: Array,
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
  },

  methods: {
    fetchData() {
      let filterOptions = {
        itemsPerPage: -1,
        descending: [false],
        sortBy: ["created_at"],
        filters: {
          project: this.localProject,
          incident: this.incident,
        },
      }

      filterOptions = SearchUtils.createParametersFromTableOptions(filterOptions)

      this.$emit("loading", "error")
      this.$emit("filterOptions", filterOptions)
      FeedbackApi.getAll(filterOptions).then((response) => {
        this.$emit("update", response.data.items)
        this.$emit("loading", false)
      })
    },
  },

  components: {
    IncidentCombobox,
    ProjectCombobox,
  },

  data() {
    return {
      display: false,
      localProject: typeof this.project === "string" ? [{ name: this.project }] : this.project,
      localIncident: typeof this.incident === "string" ? [{ name: this.incident }] : this.incident,
    }
  },

  mounted() {
    this.$watch(
      (vm) => [vm.localIncident, vm.localProject],
      () => {
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
        incident: this.localIncident,
        project: this.localProject,
      }
    },
    numFilters: function () {
      return sum([this.localIncident.length, this.localProject.length])
    },
  },
}
</script>
