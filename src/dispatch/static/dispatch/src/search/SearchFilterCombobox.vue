<template>
  <v-container>
    <v-row no-gutter>
      <v-combobox
        v-model="searchFilters"
        :items="items"
        item-text="name"
        :search-input.sync="search"
        :menu-props="{ maxHeight: '400' }"
        hide-selected
        :label="label"
        chips
        close
        clearable
        multiple
        no-filter
        :loading="loading"
        @update:search-input="getFilteredData({ q: $event })"
      >
        <template v-slot:selection="{ attr, on, item, selected }">
          <v-chip v-bind="attr" :input-value="selected" v-on="on">
            <span v-text="item.name" />
          </v-chip>
        </template>
        <template v-slot:item="{ item }">
          <v-list-item-content>
            <v-list-item-title v-text="item.name" />
            <v-list-item-subtitle v-text="item.description" />
          </v-list-item-content>
        </template>
        <template v-slot:no-data>
          <v-list-item>
            <v-list-item-content>
              <v-list-item-title>
                No filters matching "
                <strong>{{ search }}</strong>
              </v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </template>
        <template slot="append-outer">
          <search-filter-create-dialog v-model="createdFilter" />
        </template>
      </v-combobox>
    </v-row>
  </v-container>
</template>

<script>
import { cloneDeep, debounce } from "lodash"

import SearchApi from "@/search/api"
import SearchUtils from "@/search/utils"
import SearchFilterCreateDialog from "@/search/SearchFilterCreateDialog.vue"

export default {
  name: "SearchFilterCombobox",
  props: {
    value: {
      type: Array,
      default: function () {
        return []
      },
    },
    label: {
      type: String,
      default: "Search Filter",
    },
    project: {
      type: [Object],
      default: null,
    },
  },

  components: { SearchFilterCreateDialog },

  data() {
    return {
      loading: false,
      items: [],
      search: null,
      createdFilter: null,
    }
  },

  computed: {
    searchFilters: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.search = null
        this._filters = value.map((v) => {
          if (typeof v === "string") {
            v = {
              text: v,
            }
            this.items.push(v)
          }
          return v
        })
        this.$emit("input", this._filters)
      },
    },
  },

  watch: {
    createdFilter: function (newVal) {
      this.terms.append(newVal)
    },
  },

  methods: {
    fetchData() {
      this.error = null
      this.loading = "error"
      let filterOptions = {
        q: this.search,
        itemsPerPage: 50,
        sortBy: ["name"],
        descending: [false],
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

      SearchApi.getAllFilters(filterOptions).then((response) => {
        this.items = response.data.items
        this.loading = false
      })
    },
    getFilteredData: debounce(function (options) {
      this.fetchData(options)
    }, 500),
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
