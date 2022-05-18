<template>
  <v-dialog v-model="display" max-width="600px">
    <template v-slot:activator="{ on }">
      <v-badge :value="numFilters" bordered overlap color="info" :content="numFilters">
        <v-btn color="secondary" v-on="on"> Filter </v-btn>
      </v-badge>
    </template>
    <v-card>
      <v-card-title>
        <span class="headline">Data Source Filters</span>
      </v-card-title>
      <v-list dense>
        <v-list-item>
          <v-list-item-content>
            <environment-combobox v-model="local_source_environment" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <transport-combobox v-model="local_source_transport" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <data-format-combobox v-model="local_source_data_format" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <status-combobox v-model="local_source_status" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <type-combobox v-model="local_source_type" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <project-combobox v-model="local_project" label="Projects" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <tag-filter-auto-complete v-model="local_tag" label="Tags" />
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <tag-type-filter-combobox v-model="local_tag_type" label="Tag Types" />
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

import DataFormatCombobox from "@/data/source/dataFormat/DataFormatCombobox.vue"
import EnvironmentCombobox from "@/data/source/environment/EnvironmentCombobox.vue"
import ProjectCombobox from "@/project/ProjectCombobox.vue"
import StatusCombobox from "@/data/source/status/StatusCombobox.vue"
import TagFilterAutoComplete from "@/tag/TagFilterAutoComplete.vue"
import TagTypeFilterCombobox from "@/tag_type/TagTypeFilterCombobox.vue"
import TransportCombobox from "@/data/source/transport/TransportCombobox.vue"
import TypeCombobox from "@/data/source/type/TypeCombobox.vue"

export default {
  name: "SourceTableFilterDialog",

  components: {
    DataFormatCombobox,
    EnvironmentCombobox,
    ProjectCombobox,
    StatusCombobox,
    TagFilterAutoComplete,
    TagTypeFilterCombobox,
    TransportCombobox,
    TypeCombobox,
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
      local_source_data_format: [],
      local_source_environment: [],
      local_source_status: [],
      local_source_transport: [],
      local_source_type: [],
      local_tag: [],
      local_tag_type: [],
    }
  },

  computed: {
    ...mapFields("source", [
      "table.options.filters.project",
      "table.options.filters.source_data_format",
      "table.options.filters.source_environment",
      "table.options.filters.source_status",
      "table.options.filters.source_transport",
      "table.options.filters.source_type",
      "table.options.filters.tag",
      "table.options.filters.tag_type",
    ]),
    numFilters: function () {
      return sum([
        this.project.length,
        this.source_data_format.length,
        this.source_environment.length,
        this.source_status.length,
        this.source_transport.length,
        this.source_type.length,
        this.tag.length,
        this.tag_type.length,
      ])
    },
  },

  methods: {
    applyFilters() {
      // we set the filter values
      this.project = this.local_project
      this.source_data_format = this.local_source_data_format
      this.source_environment = this.local_source_environment
      this.source_status = this.local_source_status
      this.source_transport = this.local_source_transport
      this.source_type = this.local_source_type
      this.tag = this.local_tag
      this.tag_type = this.local_tag_type

      // we close the dialog
      this.display = false
    },
  },
}
</script>
