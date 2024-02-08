<template>
  <v-select
    v-model="case_severity"
    :items="items"
    item-title="name"
    :menu-props="{ maxHeight: '400' }"
    label="Severity"
    return-object
    :loading="loading"
    :rules="[is_severity_in_project]"
  >
    <template #item="data">
      <v-list-item v-bind="data.props" :title="null">
        <v-list-item-title>{{ data.item.raw.name }}</v-list-item-title>
        <v-list-item-subtitle :title="data.item.raw.description">
          {{ data.item.raw.description }}
        </v-list-item-subtitle>
      </v-list-item>
    </template>
  </v-select>
</template>

<script>
import { cloneDeep } from "lodash"

import SearchUtils from "@/search/utils"
import CaseSeverityApi from "@/case/severity/api"

export default {
  name: "CaseSeveritySelect",
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
  },

  data() {
    return {
      loading: false,
      items: [],
      error: null,
      is_severity_in_project: () => {
        this.validateSeverity()
        return this.error
      },
    }
  },

  computed: {
    case_severity: {
      get() {
        return cloneDeep(this.modelValue)
      },
      set(value) {
        this.$emit("update:modelValue", value)
        this.validateSeverity()
      },
    },
  },

  methods: {
    validateSeverity() {
      const project_id = this.project?.id || 0
      const in_project = this.case_severity?.project?.id == project_id
      if (in_project) {
        this.error = true
      } else {
        this.error = "Only severities in selected project are allowed"
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
          model: "CaseSeverity",
          field: "enabled",
          op: "==",
          value: "true",
        },
      ]

      filterOptions = SearchUtils.createParametersFromTableOptions(
        { ...filterOptions },
        enabledFilter
      )

      CaseSeverityApi.getAll(filterOptions).then((response) => {
        this.items = response.data.items
        this.loading = false
      })
    },
  },

  created() {
    this.fetchData()
    this.$watch(
      (vm) => [vm.project],
      () => {
        this.fetchData()
        this.validateSeverity()
        this.$emit("update:modelValue", this.case_severity)
      }
    )
  },
}
</script>
