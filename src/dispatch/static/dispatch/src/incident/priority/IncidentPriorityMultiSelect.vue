<template>
  <v-select
    v-model="incident_priorities"
    :items="items"
    item-title="name"
    :menu-props="{ maxHeight: '400' }"
    label="Add Incident Priorities"
    multiple
    chips
    return-object
    :loading="loading"
  />
</template>

<script>
import { cloneDeep } from "lodash"

import SearchUtils from "@/search/utils"
import IncidentPriorityApi from "@/incident/priority/api"

export default {
  name: "IncidentPriorityMultiSelect",
  props: {
    modelValue: {
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
    incident_priorities: {
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

    IncidentPriorityApi.getAll(filterOptions).then((response) => {
      this.items = response.data.items
      this.loading = false
    })
  },
}
</script>
