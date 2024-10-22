<template>
  <v-dialog v-model="display" max-width="600px">
    <template #activator="{ props }">
      <v-badge :model-value="!!numFilters" bordered color="info" :content="numFilters">
        <v-btn color="secondary" v-bind="props"> Filter </v-btn>
      </v-badge>
    </template>
    <v-card>
      <v-card-title>
        <span class="text-h5">Service Feedback Filters</span>
      </v-card-title>
      <v-list density="compact">
        <v-list-item>
          <project-combobox v-model="local_project" label="Projects" />
        </v-list-item>
        <v-list-item>
          <service-select
            v-model="local_service"
            :health-metrics="true"
            :project="local_project"
            label="Oncall service"
          />
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
import { mapFields } from "vuex-map-fields"

import ProjectCombobox from "@/project/ProjectCombobox.vue"
import ServiceSelect from "@/service/ServiceSelect.vue"

export default {
  name: "ServiceFeedbackTableFilterDialog",

  components: {
    ProjectCombobox,
    ServiceSelect,
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
      local_project: this.projects,
      local_service: null,
    }
  },

  computed: {
    ...mapFields("service_feedback", [
      "table.options.filters.project",
      "table.options.filters.schedule",
    ]),

    numFilters: function () {
      return sum([this.project.length, this.schedule ? this.schedule.length : 0])
    },
  },

  methods: {
    applyFilters() {
      // we set the filter values
      this.project = this.local_project
      if (this.local_service) {
        this.schedule = this.local_service.map((s) => s.external_id)
      } else {
        this.schedule = null
      }
      // we close the dialog
      this.display = false
    },
  },
}
</script>
