<template>
  <v-select
    v-model="incident_types"
    :items="items"
    :menu-props="{ maxHeight: '400' }"
    item-text="name"
    label="Add Incident Types"
    multiple
    chips
    return-object
    :loading="loading"
  />
</template>

<script>
import IncidentTypeApi from "@/incident_type/api"
import { cloneDeep } from "lodash"
export default {
  name: "IncidentTypeMultiSelect",

  props: {
    value: {
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

    let params = {
      itemsPerPage: 50,
      sortBy: ["name"],
      descending: [false],
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

      params = { ...params, ...{ filter: filter } }
    }

    IncidentTypeApi.getAll(params).then((response) => {
      this.items = response.data.items
      this.loading = false
    })
  },
}
</script>
