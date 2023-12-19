<template>
  <v-dialog v-model="display" max-width="600px">
    <template #activator="{ props }">
      <v-badge :model-value="!!numFilters" bordered color="info" :content="numFilters">
        <v-btn color="secondary" v-bind="props"> Filter </v-btn>
      </v-badge>
    </template>
    <v-card>
      <v-card-title>
        <span class="text-h5">Forms Filters</span>
      </v-card-title>
      <v-list density="compact">
        <v-list-item>
          <project-combobox v-model="local_project" label="Projects" />
        </v-list-item>
      </v-list>
      <v-select
        v-model="local_form_type"
        :items="enabledFormTypes"
        item-title="name"
        label="Form Type"
        multiple
        chips
        return-object
        clearable-chips
        class="ml-4 mr-4"
      />
      <v-select
        v-model="status"
        :items="['Completed', 'Draft']"
        label="Status"
        multiple
        chips
        return-object
        clearable-chips
        class="ml-4 mr-4"
      />
      <v-select
        v-model="attorney_status"
        :items="['Not reviewed', 'Reviewed: no action required', 'Reviewed: action required']"
        label="Attorney Status"
        multiple
        chips
        return-object
        clearable-chips
        class="ml-4 mr-4"
      />
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
      local_form_type: this.form_type,
    }
  },

  computed: {
    ...mapFields("forms_table", [
      "table.options.filters.project",
      "table.options.filters.forms_type",
      "table.options.filters.status",
      "table.options.filters.attorney_status",
      "form_types",
    ]),

    numFilters: function () {
      let projects = 0
      if (this.project) {
        if (Array.isArray(this.project)) {
          if (this.project.length > 0) {
            projects = 1
          }
        } else {
          projects = 1
        }
      }
      return sum([
        projects,
        this.local_form_type?.length > 0,
        this.status?.length > 0,
        this.attorney_status?.length > 0,
      ])
    },

    enabledFormTypes: function () {
      return this.form_types.filter((item) => item.enabled)
    },
  },

  methods: {
    applyFilters() {
      // we set the filter values
      this.project = this.local_project
      if (this.local_form_type && this.local_form_type.length > 0) {
        // just get the id from each of the local_form_type
        let types = []
        this.local_form_type.forEach((item) => {
          types.push({ id: item.id })
        })
        this.forms_type = types
      } else {
        this.forms_type = []
      }

      // we close the dialog
      this.display = false
    },
  },
}
</script>
