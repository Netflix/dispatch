<template>
  <v-select
    v-model="case_priority"
    :items="items"
    item-title="name"
    :menu-props="{ maxHeight: '400' }"
    label="Priority"
    return-object
    :loading="loading"
    :error-messages="show_error"
    :rules="[is_priority_in_project]"
    clearable
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
import CasePriorityApi from "@/case/priority/api"

export default {
  name: "CasePrioritySelect",
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
      is_priority_in_project: () => {
        this.validatePriority()
        return this.error
      },
    }
  },

  computed: {
    case_priority: {
      get() {
        return cloneDeep(this.modelValue)
      },
      set(value) {
        this.$emit("update:modelValue", value)
        this.validatePriority()
      },
    },
    show_error() {
      let items_names = this.items.map((item) => item.name)
      let selected_item = this.case_priority?.name || ""
      if (items_names.includes(selected_item) || selected_item == "") {
        return null
      }
      return "Not a valid case priority"
    },
  },

  methods: {
    validatePriority() {
      let in_project
      if (this.project?.name) {
        let project_name = this.project?.name || ""
        in_project = this.case_priority?.project?.name == project_name
      } else {
        let project_id = this.project?.id || 0
        in_project = this.case_priority?.project?.id == project_id
      }

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
          model: "CasePriority",
          field: "enabled",
          op: "==",
          value: "true",
        },
      ]

      filterOptions = SearchUtils.createParametersFromTableOptions(
        { ...filterOptions },
        enabledFilter
      )

      CasePriorityApi.getAll(filterOptions).then((response) => {
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
        this.validatePriority()
        this.$emit("update:modelValue", this.case_priority)
      }
    )
  },
}
</script>
