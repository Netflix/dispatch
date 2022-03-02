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
            <environment-combobox v-model="source_environment" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <transport-combobox v-model="source_transport" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <data-format-combobox v-model="source_data_format" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <status-combobox v-model="source_status" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <type-combobox v-model="source_type" />
          </v-list-item-content>
        </v-list-item>
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
import EnvironmentCombobox from "@/data/source/environment/EnvironmentCombobox.vue"
import TypeCombobox from "@/data/source/type/TypeCombobox.vue"
import DataFormatCombobox from "@/data/source/dataFormat/DataFormatCombobox.vue"
import StatusCombobox from "@/data/source/status/StatusCombobox.vue"
import TransportCombobox from "@/data/source/transport/TransportCombobox.vue"

export default {
  name: "SourceTableFilterDialog",

  components: {
    TagFilterCombobox,
    TagTypeFilterCombobox,
    ProjectCombobox,
    EnvironmentCombobox,
    StatusCombobox,
    TypeCombobox,
    TransportCombobox,
    DataFormatCombobox,
  },

  data() {
    return {
      display: false,
    }
  },

  computed: {
    ...mapFields("source", [
      "table.options.filters.tag_type",
      "table.options.filters.project",
      "table.options.filters.tag",
      "table.options.filters.source_environment",
      "table.options.filters.source_status",
      "table.options.filters.source_type",
      "table.options.filters.source_transport",
      "table.options.filters.source_data_format",
    ]),
    numFilters: function () {
      return sum([
        this.project.length,
        this.tag.length,
        this.tag_type.length,
        this.source_environment.length,
        this.source_type.length,
        this.source_status.length,
        this.source_transport.length,
        this.source_data_format.length,
      ])
    },
  },
}
</script>
