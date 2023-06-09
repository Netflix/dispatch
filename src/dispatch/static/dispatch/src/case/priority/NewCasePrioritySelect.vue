<template>
  <v-select
    v-model="case_priority"
    :items="items"
    item-text="name"
    :menu-props="{ maxHeight: '400' }"
    label="Priority"
    return-object
    :loading="loading"
  >
    <template v-slot:item="data">
      <new-case-priority :priority="data.item.name" />
    </template>
  </v-select>
</template>
<script>
import { cloneDeep } from "lodash"

import SearchUtils from "@/search/utils"
import CasePriorityApi from "@/case/priority/api"
import NewCasePriority from "@/case/priority/NewCasePriority.vue"

export default {
  name: "NewCasePrioritySelect",
  components: {
    NewCasePriority,
  },
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
  },

  data() {
    return {
      loading: false,
      items: [],
    }
  },

  computed: {
    case_priority: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.$emit("input", value)
      },
    },
  },

  methods: {
    fetchData() {
      this.error = null
      this.loading = true

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
      }
    )
  },
}
</script>
