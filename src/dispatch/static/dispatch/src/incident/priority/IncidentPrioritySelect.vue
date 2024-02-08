<template>
  <v-select
    v-model="incident_priorities"
    :items="items"
    item-title="name"
    :item-props="(item) => ({ subtitle: item.description })"
    :menu-props="{ maxHeight: '400' }"
    label="Priority"
    return-object
    :loading="loading"
    :error-messages="show_error"
    :rules="[is_priority_in_project]"
  />
</template>

<script>
import { cloneDeep } from "lodash"

import SearchUtils from "@/search/utils"
import IncidentPriorityApi from "@/incident/priority/api"

export default {
  name: "IncidentPrioritySelect",
  props: {
    modelValue: {
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
      error: null,
      is_priority_in_project: () => {
        this.validatePriority()
        return this.error
      },
    }
  },

  computed: {
    incident_priorities: {
      get() {
        return cloneDeep(this.modelValue)
      },
      set(value) {
        this.$emit("update:modelValue", value)
        this.validatePriority()
      },
    },
    show_error() {
      if (!this.project) return null
      const stablePriority = this.project.stable_priority
      if (!stablePriority) return null
      if (this.status == "Stable" && this.modelValue.name != stablePriority.name) {
        return `Priority must be ${stablePriority.name} for Stable incidents`
      }
      return null
    },
  },

  methods: {
    validatePriority() {
      const project_id = this.project?.id || 0
      const in_project = this.incident_priorities?.project?.id == project_id
      if (in_project) {
        this.error = true
      } else {
        this.error = "Only priorities in selected project are allowed"
      }
    },
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
        this.validatePriority()
        this.$emit("update:modelValue", this.incident_priorities)
      }
    )
  },
}
</script>
