<template>
  <v-combobox
    :items="items"
    :label="label"
    :loading="loading"
    :search-input.sync="search"
    @update:search-input="getFilteredData()"
    chips
    clearable
    deletable-chips
    hide-selected
    item-text="name"
    item-value="id"
    multiple
    no-filter
    v-model="cases"
  >
    <template v-slot:no-data>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title>
            No cases matching "
            <strong>{{ search }}</strong
            >"
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </template>
    <template v-slot:item="data">
      <template>
        <v-list-item-content>
          <v-list-item-title v-text="data.item.name" />
          <v-list-item-subtitle
            style="width: 200px"
            class="text-truncate"
            v-text="data.item.title"
          />
        </v-list-item-content>
      </template>
    </template>
    <template v-slot:append-item>
      <v-list-item v-if="more" @click="loadMore()">
        <v-list-item-content>
          <v-list-item-subtitle> Load More </v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>
    </template>
  </v-combobox>
</template>

<script>
import { cloneDeep, debounce } from "lodash"

import CaseApi from "@/case/api"
import SearchUtils from "@/search/utils"

export default {
  name: "CaseFilterSelect",

  props: {
    value: {
      type: Object,
      default: function () {
        return {}
      },
    },
    label: {
      type: String,
      default: "Add Case",
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
    cases: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.search = null
        this._cases = value.filter((v) => {
          if (typeof v === "string") {
            return false
          }
          return true
        })
        this.$emit("input", this._cases)
      },
    },
  },

  created() {
    this.fetchData()
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
        sortBy: ["name"],
        descending: [false],
        itemsPerPage: this.numItems,
      }

      if (this.project) {
        filterOptions = {
          ...filterOptions,
          filters: {
            project: [this.project],
          },
        }
        filterOptions = SearchUtils.createParametersFromTableOptions({ ...filterOptions })
      }
      CaseApi.getAll(filterOptions).then((response) => {
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
