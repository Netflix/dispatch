<template>
  <v-container>
    <v-row no-gutter>
      <v-combobox
        :items="items"
        :label="label"
        :loading="loading"
        :menu-props="{ maxHeight: '400' }"
        :search-input.sync="search"
        @update:search-input="getFilteredData({ q: $event })"
        chips
        clearable
        close
        deletable-chips
        hide-selected
        item-text="name"
        item-value="id"
        multiple
        no-filter
        v-model="searchFilters"
      >
        <template v-slot:selection="{ attr, item, selected }">
          <v-menu v-model="menu" bottom right transition="scale-transition" origin="top left">
            <template v-slot:activator="{ on }">
              <v-chip v-bind="attr" :input-value="selected" pill v-on="on">
                {{ item.name }}
              </v-chip>
            </template>
            <v-card>
              <v-list dark>
                <v-list-item>
                  <v-list-item-avatar color="teal">
                    <span class="white--text">{{ item.name | initials }}</span>
                  </v-list-item-avatar>
                  <v-list-item-content>
                    <v-list-item-title>{{ item.name }}</v-list-item-title>
                    <v-list-item-subtitle>{{ item.type }}</v-list-item-subtitle>
                  </v-list-item-content>
                  <v-list-item-action>
                    <v-btn icon @click="menu = false">
                      <v-icon>mdi-close-circle</v-icon>
                    </v-btn>
                  </v-list-item-action>
                </v-list-item>
              </v-list>
              <v-list>
                <v-list-item>
                  <v-list-item-action>
                    <v-icon>mdi-text-box</v-icon>
                  </v-list-item-action>
                  <v-list-item-subtitle>{{ item.description }}</v-list-item-subtitle>
                </v-list-item>
                <v-list-item v-if="item.expression">
                  <v-list-item-action>
                    <v-icon>mdi-code-json</v-icon>
                  </v-list-item-action>
                  <v-list-item-subtitle>
                    <pre>{{ item.expression }}</pre>
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-card>
          </v-menu>
        </template>
        <template v-slot:item="{ item }">
          <v-list-item-content>
            <v-list-item-title v-text="item.name" />
            <v-list-item-subtitle
              style="width: 200px"
              class="text-truncate"
              v-text="item.description"
            />
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
      menu: false,
    }
  },

  computed: {
    searchFilters: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.search = null
        this._filters = value.filter((v) => {
          if (typeof v === "string") {
            return false
          }
          return true
        })
        this.$emit("input", this._filters)
      },
    },
  },

  watch: {
    createdFilter: function (newVal) {
      this.items.push(newVal)
      this.searchFilters = [newVal]
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
