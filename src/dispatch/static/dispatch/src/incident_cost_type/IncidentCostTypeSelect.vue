<template>
  <v-select
    v-model="incident_cost_type"
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
import IncidentCostTypeApi from "@/incident_cost_type/api"
import { cloneDeep, debounce } from "lodash"
export default {
  name: "IncidentCostTypeSelect",

  props: {
    value: {
      type: Object,
      default: function () {
        return {}
      },
    },
    project: {
      type: String,
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
    incident_cost_type: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.$emit("input", value)
      },
    },
  },

  created() {
    this.fetchData({
      filter: JSON.stringify({
        and: [
          {
            field: "editable",
            op: "==",
            value: "true",
          },
        ],
      }),
    })
  },

  methods: {
    fetchData(filterOptions) {
      this.error = null
      this.loading = "error"
      IncidentCostTypeApi.getAll(filterOptions).then((response) => {
        this.items = response.data.items
        this.loading = false
      })
    },
    getFilteredData: debounce(function (options) {
      this.fetchData(options)
    }, 500),
  },
}
</script>
