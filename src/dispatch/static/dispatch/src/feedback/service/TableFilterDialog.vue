<template>
  <v-dialog v-model="display" max-width="600px">
    <template #activator="{ on }">
      <v-badge :value="numFilters" bordered overlap color="info" :content="numFilters">
        <v-btn color="secondary" v-on="on"> Filter </v-btn>
      </v-badge>
    </template>
    <v-card>
      <v-card-title>
        <span class="headline">Service Feedback Filters</span>
      </v-card-title>
      <v-list dense>
        <v-list-item>
          <v-list-item-content>
            <project-combobox v-model="local_project" label="Projects" />
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

import ProjectCombobox from "@/project/ProjectCombobox.vue"

export default {
  name: "ServiceFeedbackTableFilterDialog",

  components: {
    ProjectCombobox,
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
    }
  },

  computed: {
    ...mapFields("service_feedback", ["table.options.filters.project"]),

    numFilters: function () {
      return sum([this.project.length])
    },
  },

  methods: {
    applyFilters() {
      // we set the filter values
      this.project = this.local_project

      // we close the dialog
      this.display = false
    },
  },
}
</script>
