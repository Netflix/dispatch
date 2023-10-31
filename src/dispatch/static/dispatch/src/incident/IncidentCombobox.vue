<template>
  <v-combobox
    :items="items"
    :label="label"
    :loading="loading"
    :menu-props="{ maxHeight: '400' }"
    v-model:search="search"
    @update:search="fetchData({ q: $event })"
    chips
    clearable
    closable-chips
    hide-selected
    item-title="name"
    item-value="id"
    multiple
    no-filter
    v-model="incident"
  >
    <template #item="{ item, props }">
      <v-list-item v-bind="props" :title="null">
        <v-list-item-title>{{ item.raw.name }}</v-list-item-title>
        <v-list-item-subtitle :title="item.raw.title">
          {{ item.raw.title }}
        </v-list-item-subtitle>
      </v-list-item>
    </template>
    <template #no-data>
      <v-list-item>
        <v-list-item-title>
          No incidents matching "<strong>{{ search }}</strong
          >".
        </v-list-item-title>
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
    modelValue: {
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
        return cloneDeep(this.modelValue)
      },
      set(value) {
        const incidents = value.filter((v) => {
          if (typeof v === "string") {
            return false
          }
          return true
        })
        this.$emit("update:modelValue", incidents)
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
