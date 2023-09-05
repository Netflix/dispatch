<template>
  <v-select
    v-model="incident_priorities"
    :items="items"
    item-text="name"
    :menu-props="{ maxHeight: '400' }"
    label="Priority"
    return-object
    :loading="loading"
    :error-messages="show_error"
  >
    <template #item="data">
      <template>
        <v-list-item-content>
          <v-list-item-title>{{ data.item.name }}</v-list-item-title>
          <v-list-item-subtitle>{{ data.item.description }}</v-list-item-subtitle>
        </v-list-item-content>
      </template>
    </template>
  </v-select>
</template>

<script>
import { cloneDeep } from "lodash"

import SearchUtils from "@/search/utils"
import IncidentPriorityApi from "@/incident/priority/api"

export default {
  name: "IncidentPrioritySelect",
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
    status: {
      type: String,
      default: "",
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
        return cloneDeep(this.value)
      },
      set(value) {
        this.$emit("input", value)
      },
    },
    show_error() {
      if (!this.project) return null
      const restrictStableTo = this.project.restrict_stable_to
      if (!restrictStableTo) return null
      if (this.status == "Stable" && this.value.name != restrictStableTo.name) {
        return `Priority must be ${restrictStableTo.name} for Stable incidents`
      }
      return null
    },
  },

  methods: {
    fetchData() {
      this.error = null
      this.loading = "error"

      let filterOptions = {
        sortBy: ["view_order"],
        descending: [false],
      }

      if (this.project) {
        filterOptions = {
          ...filterOptions,
          filters: {
            project: [this.project],
          },
        }
      }

      let enabledFilter = [
        {
          model: "IncidentPriority",
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
  },

  created() {
    this.fetchData()
    this.$watch(
      (vm) => [vm.project, vm.status],
      () => {
        this.fetchData()
      }
    )
  },
}
</script>
