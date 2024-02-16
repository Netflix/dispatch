<template>
  <v-select
    v-model="case_type"
    :items="items"
    :menu-props="{ maxHeight: '400' }"
    item-title="name"
    item-value="id"
    :label="label"
    :hint="hint"
    return-object
    :loading="loading"
    no-filter
    :error-messages="show_error"
    :rules="[is_type_in_project]"
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
    <template #append-item>
      <v-list-item v-if="more" @click="loadMore()">
        <v-list-item-subtitle> Load More </v-list-item-subtitle>
      </v-list-item>
    </template>
  </v-select>
</template>

<script>
import { cloneDeep } from "lodash"

import SearchUtils from "@/search/utils"
import CaseTypeApi from "@/case/type/api"

export default {
  name: "CaseTypeSelect",

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
    hint: {
      type: String,
      default: function () {
        return "Case Type to associate"
      },
    },
    label: {
      type: String,
      default: function () {
        return "Case Type"
      },
    },
  },

  data() {
    return {
      loading: false,
      items: [],
      search: null,
      more: false,
      numItems: 5,
      error: null,
      is_type_in_project: () => {
        this.validateType()
        return this.error
      },
    }
  },

  computed: {
    case_type: {
      get() {
        return cloneDeep(this.modelValue)
      },
      set(value) {
        this.$emit("update:modelValue", value)
        this.validateType()
      },
    },
    show_error() {
      let items_names = this.items.map((item) => item.name)
      let selected_item = this.case_type?.name || ""
      if (items_names.includes(selected_item) || selected_item == "") {
        return null
      }
      return "Not a valid case type"
    },
  },

  methods: {
    loadMore() {
      this.numItems = this.numItems + 5
      this.fetchData()
    },
    validateType() {
      let in_project
      if (this.project?.name) {
        let project_name = this.project?.name || ""
        in_project = this.case_type?.project?.name == project_name
      } else {
        let project_id = this.project?.id || 0
        in_project = this.case_type?.project?.id == project_id
      }

      if (in_project) {
        this.error = true
      } else {
        this.error = "Only types in selected project are allowed"
      }
    },
    fetchData() {
      this.error = null
      this.loading = "error"

      let filterOptions = {
        q: "",
        sortBy: ["name"],
        descending: [false],
        itemsPerPage: -1,
      }

      if (this.project) {
        filterOptions = {
          filters: {
            project: [this.project],
            enabled: ["true"],
          },
          ...filterOptions,
        }
      }

      filterOptions = SearchUtils.createParametersFromTableOptions({ ...filterOptions })

      if (this.items.length == 0) {
        CaseTypeApi.getAll(filterOptions).then((response) => {
          this.items = response.data.items
        })
      }
      filterOptions.itemsPerPage = this.numItems
      CaseTypeApi.getAll(filterOptions).then((response) => {
        this.total = response.data.total
        this.loading = false

        if (this.items.length < this.total) {
          this.more = true
        } else {
          this.more = false
        }
      })
    },
  },

  watch: {
    search(val) {
      val && val !== this.select && this.fetchData()
    },
    value(val) {
      if (!val) return
      this.items.push(val)
    },
  },

  created() {
    this.fetchData()
    this.$watch(
      (vm) => [vm.project],
      () => {
        this.fetchData()
        this.validateType()
        this.$emit("update:modelValue", this.case_type)
      }
    )
  },
}
</script>
