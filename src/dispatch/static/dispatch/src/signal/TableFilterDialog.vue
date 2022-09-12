<template>
  <v-dialog v-model="display" max-width="600px">
    <template v-slot:activator="{ on }">
      <v-badge :value="numFilters" bordered overlap color="info" :content="numFilters">
        <v-btn color="secondary" v-on="on"> Filter </v-btn>
      </v-badge>
    </template>
    <v-card>
      <v-card-title>
        <span class="headline">Signal Filters</span>
      </v-card-title>
      <v-list dense>
        <v-list-item>
          <v-list-item-content>
            <date-window-input v-model="local_created_at" label="Created At" />
          </v-list-item-content>
        </v-list-item>
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

import DateWindowInput from "@/components/DateWindowInput.vue"
import ProjectCombobox from "@/project/ProjectCombobox.vue"

export default {
  name: "SignalTableFilterDialog",

  components: {
    DateWindowInput,
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
      local_created_at: {},
      local_project: this.projects,
    }
  },

  computed: {
    ...mapFields("signal", ["table.options.filters.created_at", "table.options.filters.project"]),
    numFilters: function () {
      return sum([this.project.length])
    },
  },

  methods: {
    applyFilters() {
      // we set the filter values
      this.created_at = this.local_created_at
      this.project = this.local_project

      // we close the dialog
      this.display = false
    },
  },
}
</script>
