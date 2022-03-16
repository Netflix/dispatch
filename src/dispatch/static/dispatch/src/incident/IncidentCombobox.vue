<template>
  <v-combobox
    :items="items"
    :label="label"
    :loading="loading"
    :menu-props="{ maxHeight: '400' }"
    :search-input.sync="search"
    @update:search-input="fetchData({ q: $event })"
    chips
    clearable
    deletable-chips
    hide-selected
    item-text="name"
    item-value="id"
    multiple
    no-filter
    v-model="incident"
  >
    <template v-slot:selection="{ attr, on, item, selected }">
      <v-chip v-bind="attr" :input-value="selected" v-on="on">
        <span v-text="item.name" />
      </v-chip>
    </template>
    <template v-slot:item="{ item }">
      <v-list-item-content>
        <v-list-item-title v-text="item.name" />
        <v-list-item-subtitle style="width: 200px" class="text-truncate" v-text="item.title" />
      </v-list-item-content>
    </template>
    <template v-slot:no-data>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title>
            No incidents matching "
            <strong>{{ search }}</strong
            >".
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </template>
  </v-combobox>
</template>

<script>
import IncidentApi from "@/incident/api"
import { cloneDeep, debounce } from "lodash"
export default {
  name: "IncidentComboBox",
  props: {
    value: {
      type: Array,
      default: function () {
        return []
      },
    },
    label: {
      type: String,
      default: function () {
        return "Incident"
      },
    },
  },

  data() {
    return {
      loading: false,
      items: [],
      search: null,
    }
  },

  computed: {
    incident: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this._incidents = value.filter((v) => {
          if (typeof v === "string") {
            return false
          }
          return true
        })
        this.$emit("input", this._incidents)
        this.search = null
      },
    },
  },

  created() {
    this.fetchData({})
  },

  methods: {
    fetchData(filterOptions) {
      this.error = null
      this.loading = "error"
      IncidentApi.getAll(filterOptions).then((response) => {
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
