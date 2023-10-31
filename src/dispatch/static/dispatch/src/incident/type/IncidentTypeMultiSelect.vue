<template>
  <v-select
    v-model="incident_types"
    :items="items"
    :menu-props="{ maxHeight: '400' }"
    item-title="name"
    label="Add Incident Types"
    multiple
    chips
    return-object
    :loading="loading"
  />
</template>

<script>
import { cloneDeep } from "lodash"

import SearchUtils from "@/search/utils"
import IncidentTypeApi from "@/incident/type/api"

export default {
  name: "IncidentTypeMultiSelect",

  props: {
    modelValue: {
      type: Array,
      default: function () {
        return []
      },
    },
    visibilities: {
      type: Array,
      default: function () {
        return []
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
    incident_types: {
      get() {
        return cloneDeep(this.modelValue)
      },
      set(value) {
        this.$emit("update:modelValue", value)
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
      filters: {
        project: [this.project],
      },
    }

    if (this.visibilities.length) {
      let filter = { and: [] }

      this.visibilities.forEach(function (item) {
        filter.and.push({
          field: "visibility",
          op: "==",
          value: item,
        })
      })

      filterOptions = { ...filterOptions, ...{ filter: filter } }
    }

    let enabledFilter = [
      {
        model: "IncidentType",
        field: "enabled",
        op: "==",
        value: "true",
      },
    ]

    filterOptions = SearchUtils.createParametersFromTableOptions(
      { ...filterOptions },
      enabledFilter
    )

    IncidentTypeApi.getAll(filterOptions).then((response) => {
      this.items = response.data.items
      this.loading = false
    })
  },
}
</script>
