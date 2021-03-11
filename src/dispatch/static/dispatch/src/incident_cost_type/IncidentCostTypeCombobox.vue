<template>
  <v-combobox
    v-model="incident_cost_types"
    :items="items"
    :search-input.sync="search"
    hide-selected
    :label="label"
    multiple
    chips
    :loading="loading"
    @update:search-input="getFilteredData({ q: $event })"
  >
    <template v-slot:no-data>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title>
            No incident type costs matching "
            <strong>{{ search }}</strong
            >". Press <kbd>enter</kbd> to create a new one.
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </template>
  </v-combobox>
</template>

<script>
import IncidentCostTypeApi from "@/incident_cost_type/api"
import { cloneDeep, debounce } from "lodash"
export default {
  name: "IncidentCostTypeCombobox",
  props: {
    value: {
      type: Array,
      default: function() {
        return []
      }
    },
    label: {
      type: String,
      default: "Add Incident Cost Types"
    }
  },
  data() {
    return {
      loading: false,
      items: [],
      search: null
    }
  },

  computed: {
    incident_cost_types: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.search = null
        this._incident_cost_types = value.map(v => {
          if (typeof v === "string") {
            v = {
              text: v
            }
            this.items.push(v)
          }
          return v
        })
        this.$emit("input", this._incident_cost_types)
      }
    }
  },

  created() {
    this.fetchData({})
  },

  methods: {
    fetchData(filterOptions) {
      this.error = null
      this.loading = "error"
      IncidentCostTypeApi.getAll(filterOptions).then(response => {
        this.items = response.data.items
        this.loading = false
      })
    },
    getFilteredData: debounce(function(options) {
      this.fetchData(options)
    }, 500)
  }
}
</script>
