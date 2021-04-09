<template>
  <v-select
    v-model="incident_type"
    :items="items"
    :menu-props="{ maxHeight: '400' }"
    item-text="name"
    label="Type"
    return-object
    :loading="loading"
  >
    <template v-slot:item="data">
      <v-list-item-content>
        <v-list-item-title v-text="data.item.name" />
        <v-list-item-subtitle v-text="data.item.description" />
      </v-list-item-content>
    </template>
  </v-select>
</template>

<script>
import { cloneDeep } from "lodash"

import SearchUtils from "@/search/utils"
import IncidentTypeApi from "@/incident_type/api"

export default {
  name: "IncidentTypeSelect",

  props: {
    value: {
      type: Object,
      default: function () {
        return {}
      },
    },
    project: {
      type: [Object],
      default: null,
    },
  },

  data() {
    return {
      loading: false,
      items: [],
    }
  },

  computed: {
    incident_type: {
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
      filterOptions = SearchUtils.createParametersFromTableOptions(filterOptions)
    }

    IncidentTypeApi.getAll(filterOptions).then((response) => {
      this.items = response.data.items
      this.loading = false
    })
  },
}
</script>
