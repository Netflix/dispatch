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
            <project-combobox v-model="project" label="Projects" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <tag-filter-combobox v-model="tag" label="Tags" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <tag-type-filter-combobox v-model="tag_type" label="Tag Types" />
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-card>
  </v-dialog>
</template>

<script>
import { sum } from "lodash"
import { mapFields } from "vuex-map-fields"
import TagFilterCombobox from "@/tag/TagFilterCombobox.vue"
import TagTypeFilterCombobox from "@/tag_type/TagTypeFilterCombobox.vue"
import ProjectCombobox from "@/project/ProjectCombobox.vue"

export default {
  name: "QueryTableFilterDialog",

  components: {
    TagFilterCombobox,
    TagTypeFilterCombobox,
    ProjectCombobox,
  },

  data() {
    return {
      display: false,
    }
  },

  computed: {
    ...mapFields("query", [
      "table.options.filters.tag_type",
      "table.options.filters.project",
      "table.options.filters.tag",
    ]),
    numFilters: function () {
      return sum([this.project.length, this.tag.length, this.tag_type.length])
    },
  },
}
</script>
