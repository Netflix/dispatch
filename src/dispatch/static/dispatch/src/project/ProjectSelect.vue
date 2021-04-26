<template>
  <v-select
    v-model="project"
    :items="items"
    :menu-props="{ maxHeight: '400' }"
    item-text="name"
    label="Project"
    return-object
    :loading="loading"
  >
    <template v-slot:item="data">
      <v-list-item-content>
        <v-list-item-title v-text="data.item.name" />
        <v-list-item-subtitle
          style="width: 200px"
          class="text-truncate"
          v-text="data.item.description"
        />
      </v-list-item-content>
    </template>
  </v-select>
</template>

<script>
import { cloneDeep } from "lodash"

import SearchUtils from "@/search/utils"
import ProjectApi from "@/project/api"

export default {
  name: "ProjectSelect",

  props: {
    value: {
      type: Object,
      default: function () {
        return {}
      },
    },
  },

  data() {
    return {
      loading: false,
      items: [],
    }
  },

  computed: {
    project: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.$emit("input", value)
      },
    },
  },

  created() {
    this.error = null
    this.loading = "error"
    let filterOptions = {
      itemsPerPage: 50,
      sortBy: ["name"],
      descending: [false],
    }

    if (this.project) {
      filterOptions = {
        ...filterOptions,
        filters: {
          project: [this.project],
        },
      }
      filterOptions = SearchUtils.createParametersFromTableOptions({ ...filterOptions })
    }

    ProjectApi.getAll(filterOptions).then((response) => {
      this.items = response.data.items
      this.loading = false
    })
  },
}
</script>
