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
    v-model="incidentType"
  >
    <template #no-data>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title>
            No incident types matching "
            <strong>{{ search }}</strong
            >".
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </template>
    <template #selection="{ item, index }">
      <v-chip close @click:close="remove(index)">
        <span v-if="!project"
          ><span v-if="item.project">{{ item.project.name }}/</span></span
        >{{ item.name }}
      </v-chip>
    </template>
    <template #item="data">
      <template>
        <v-list-item-content>
          <v-list-item-title>
            <span v-if="!project"
              ><span v-if="data.item.project">{{ data.item.project.name }}/</span></span
            >{{ data.item.name }}
          </v-list-item-title>
          <v-list-item-subtitle style="width: 200px" class="text-truncate">
            {{ data.item.description }}
          </v-list-item-subtitle>
        </v-list-item-content>
      </template>
    </template>
    <template #append-item>
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

import SearchUtils from "@/search/utils"
import IncidentTypeApi from "@/incident/type/api"

export default {
  name: "IncidentTypeComboBox",

  props: {
    value: {
      type: Array,
      default: function () {
        return []
      },
    },
    label: {
      type: String,
      default: function () {
        return "Types"
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
      more: false,
      numItems: 5,
      search: null,
    }
  },

  computed: {
    incidentType: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.search = null
        const incidentTypes = value.filter((v) => {
          if (typeof v === "string") {
            return false
          }
          return true
        })
        this.$emit("input", incidentTypes)
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
      }

      let enabledFilter = [
        {
          model: "IncidentType",
          field: "enabled",
          op: "==",
          value: "true",
        },
      ]

      filterOptions = SearchUtils.createParametersFromTableOptions(
        { ...filterOptions },
        enabledFilter
      )

      IncidentTypeApi.getAll(filterOptions).then((response) => {
        this.items = response.data.items
        this.total = response.data.total
        this.loading = false

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
    remove(index) {
      const value = cloneDeep(this.value)
      value.splice(index, 1)
      this.$emit("input", value)
    },
  },
}
</script>
