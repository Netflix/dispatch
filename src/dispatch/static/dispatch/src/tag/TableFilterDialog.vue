<template>
  <v-dialog v-model="display" max-width="600px">
    <template #activator="{ props }">
      <v-badge :model-value="!!numFilters" bordered color="info" :content="numFilters">
        <v-btn color="secondary" v-bind="props"> Filter </v-btn>
      </v-badge>
    </template>
    <v-card>
      <v-card-title>
        <span class="text-h5">Tag Filters</span>
      </v-card-title>
      <v-list density="compact">
        <v-list-item>
          <tag-type-filter-combobox
            v-model="local_tag_type"
            label="Tag Types"
            :project="currentProject"
          />
        </v-list-item>
        <v-list-item>
          <v-select
            v-model="local_discoverable"
            :items="discoverableOptions"
            item-title="text"
            item-value="value"
            label="Discoverable"
            clearable
            multiple
            chips
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

import TagTypeFilterCombobox from "@/tag_type/TagTypeFilterCombobox.vue"

export default {
  name: "TagTableFilterDialog",

  components: {
    TagTypeFilterCombobox,
  },

  props: {
    project: {
      type: Array,
      default: function () {
        return []
      },
    },
  },

  data() {
    return {
      display: false,
      local_tag_type: [],
      local_discoverable: [],
      discoverableOptions: [
        { text: "True", value: true },
        { text: "False", value: false },
      ],
    }
  },

  computed: {
    ...mapFields("tag", ["table.options.filters.tag_type", "table.options.filters.discoverable"]),
    currentProject() {
      // TagTypeFilterCombobox expects a single project object, not an array
      return this.project && this.project.length > 0 ? this.project[0] : null
    },
    numFilters: function () {
      return sum([this.tag_type?.length || 0, this.discoverable?.length || 0])
    },
  },

  methods: {
    applyFilters() {
      // Debug logging
      console.log("Applying filters:")
      console.log("local_tag_type:", this.local_tag_type)
      console.log("local_discoverable:", this.local_discoverable)

      // Check the structure of tag_type objects
      if (this.local_tag_type && this.local_tag_type.length > 0) {
        console.log("First tag_type object:", this.local_tag_type[0])
        console.log("Has id?", this.local_tag_type[0].id)
        console.log("Has name?", this.local_tag_type[0].name)
      }

      // we set the filter values
      this.tag_type = this.local_tag_type
      this.discoverable = this.local_discoverable

      // Debug: Check what's in the store after setting filters
      console.log("After setting filters:")
      console.log("Store tag_type:", this.tag_type)
      console.log("Store discoverable:", this.discoverable)

      // we close the dialog
      this.display = false
    },
  },
}
</script>
