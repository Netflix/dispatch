<template>
  <v-dialog v-model="display" max-width="600px">
    <template #activator="{ props }">
      <v-badge :model-value="!!numFilters" bordered color="info" :content="numFilters">
        <v-btn color="secondary" v-bind="props"> Filter </v-btn>
      </v-badge>
    </template>
    <v-card>
      <v-card-title>
        <span class="text-h5">Data Query Filters</span>
      </v-card-title>
      <v-list density="compact">
        <v-list-item>
          <project-combobox v-model="local_project" label="Projects" />
        </v-list-item>
        <v-list-item>
          <tag-type-filter-combobox v-model="local_tag_type" label="Tag Types" />
        </v-list-item>
        <v-list-item>
          <tag-filter-auto-complete
            v-model="local_tag"
            label="Tags"
            model="query"
            :project="local_project"
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
import TagFilterAutoComplete from "@/tag/TagPicker.vue"
import TagTypeFilterCombobox from "@/tag_type/TagTypeFilterCombobox.vue"

export default {
  name: "QueryTableFilterDialog",

  components: {
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
      local_project: this.projects,
      local_tag_type: [],
      local_tag: [],
    }
  },

  computed: {
    ...mapFields("query", [
      "table.options.filters.project",
      "table.options.filters.tag_type",
      "table.options.filters.tag",
    ]),
    numFilters: function () {
      return sum([this.project.length, this.tag.length, this.tag_type.length])
    },
  },

  methods: {
    applyFilters() {
      // we set the filter values
      this.project = this.local_project
      this.tag_type = this.local_tag_type
      this.tag = this.local_tag

      // we close the dialog
      this.display = false
    },
  },
}
</script>
