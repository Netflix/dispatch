<template>
  <v-combobox
    :items="items"
    :label="label"
    :loading="loading"
    v-model:search="search"
    @update:search="getFilteredData()"
    chips
    clearable
    closable-chips
    hide-selected
    :hide-no-data="!search"
    item-title="name"
    item-value="id"
    multiple
    no-filter
    v-model="project"
    :menu-props="{ maxWidth: 0 }"
  >
    <template #no-data>
      <v-list-item v-if="search">
        <v-list-item-title>
          No Projects matching "<strong>{{ search }}</strong
          >".
        </v-list-item-title>
      </v-list-item>
    </template>
    <template #item="{ props, item }">
      <v-list-item v-bind="props">
        <v-list-item-subtitle :title="item.raw.description">
          {{ item.raw.description }}
        </v-list-item-subtitle>
      </v-list-item>
    </template>
    <template #append-item>
      <v-list-item v-if="more" @click="loadMore()">
        <v-list-item-subtitle> Load More </v-list-item-subtitle>
      </v-list-item>
    </template>
  </v-combobox>
</template>

<script>
import { cloneDeep, debounce } from "lodash"

import SearchUtils from "@/search/utils"
import ProjectApi from "@/project/api"

export default {
  name: "ProjectComboBox",

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
        return "Projects"
      },
    },
  },

  data() {
    return {
      loading: false,
      items: [],
      more: false,
      numItems: 5,
      search: null,
    }
  },

  computed: {
    project: {
      get() {
        return cloneDeep(this.modelValue)
      },
      set(value) {
        this.search = null
        let _projects = value.filter((v) => {
          if (typeof v === "string") {
            return false
          }
          return true
        })
        this.$emit("update:modelValue", _projects)
      },
    },
  },

  created() {
    this.fetchData({})
  },

  methods: {
    loadMore() {
      this.numItems = this.numItems + 5
      this.fetchData()
    },
    fetchData() {
      this.error = null
      this.loading = "error"

      let filterOptions = {
        q: this.search,
        itemsPerPage: this.numItems,
        sortBy: ["name"],
        descending: [false],
      }

      filterOptions = SearchUtils.createParametersFromTableOptions({ ...filterOptions })

      ProjectApi.getAll(filterOptions).then((response) => {
        this.items = response.data.items
        this.total = response.data.total

        if (this.items.length < this.total) {
          this.more = true
        } else {
          this.more = false
        }

        this.loading = false
      })
    },
    getFilteredData: debounce(function () {
      this.fetchData()
    }, 500),
  },
}
</script>
