<template>
  <v-combobox
    v-model="service"
    :items="items"
    v-model:search="search"
    :menu-props="{ maxHeight: '400' }"
    item-title="name"
    item-value="id"
    :label="label"
    placeholder="Start typing to search"
    return-object
    :hint="hint"
    :loading="loading"
    no-filter
    clearable
    chips
    multiple
    closable-chips
  >
    <template #append-item>
      <v-list-item v-if="more" @click="loadMore">
        <v-list-item-subtitle>Load More</v-list-item-subtitle>
      </v-list-item>
    </template>
  </v-combobox>
</template>

<script>
import { cloneDeep } from "lodash"
import { debounce } from "lodash"
import SearchUtils from "@/search/utils"
import ServiceApi from "@/service/api"

export default {
  name: "ServiceSelect",

  props: {
    modelValue: {
      type: Object,
      default: function () {
        return null
      },
    },
    label: {
      type: String,
      default: function () {
        return "Service"
      },
    },
    hint: {
      type: String,
      default: function () {
        return "Service to associate"
      },
    },
    project: {
      type: Object,
      default: null,
    },
    healthMetrics: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      loading: false,
      search: null,
      select: null,
      items: [],
      more: false,
      numItems: 5,
      total: 0,
    }
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

  computed: {
    service: {
      get() {
        return cloneDeep(this.modelValue)
      },
      set(value) {
        this.$emit("update:modelValue", value)
      },
    },
  },

  methods: {
    loadMore() {
      this.numItems += 5
      this.fetchData()
    },
    fetchData: debounce(function () {
      this.error = null
      this.loading = "error"
      let filterOptions = {
        q: this.search,
        sortBy: ["name"],
        descending: [false],
        itemsPerPage: this.numItems,
        filters: { is_active: ["true"] },
      }

      if (this.project) {
        filterOptions.filters.project_id = this.project.map((p) => p.id)
      }

      if (this.healthMetrics) {
        filterOptions.filters.health_metrics = ["true"]
      }

      filterOptions = SearchUtils.createParametersFromTableOptions({ ...filterOptions })

      ServiceApi.getAll(filterOptions).then((response) => {
        this.items = response.data.items
        this.total = response.data.total
        this.more = this.items.length < this.total
        this.loading = false
      })
    }, 300),
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
