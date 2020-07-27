<template>
  <v-combobox
    v-model="incidentPriority"
    :items="items"
    item-text="name"
    :search-input.sync="search"
    :menu-props="{ maxHeight: '400' }"
    hide-selected
    :label="label"
    multiple
    chips
    clearable
    :loading="loading"
    @update:search-input="fetchData({ q: $event })"
  >
    <template v-slot:no-data>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title>
            No Incident Priorities matching "
            <strong>{{ search }}</strong
            >".
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </template>
  </v-combobox>
</template>

<script>
import IncidentPriorityApi from "@/incident_priority/api"
import { cloneDeep, debounce } from "lodash"
export default {
  name: "IncidentPriorityComboBox",
  props: {
    value: {
      priority: Array,
      default: function() {
        return []
      }
    },
    label: {
      priority: String,
      default: function() {
        return "Priorities"
      }
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
    incidentPriority: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.search = null
        this._incidentPriorities = value.map(v => {
          if (typeof v === "string") {
            v = {
              name: v
            }
            this.items.push(v)
          }
          return v
        })
        this.$emit("input", this._incidentPriorities)
      }
    }
  },

  created() {
    this.fetchData({})
  },

  methods: {
    fetchData(filterOptions) {
      this.error = null
      this.loading = true
      IncidentPriorityApi.getAll(filterOptions).then(response => {
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
