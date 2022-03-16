<template>
  <v-combobox
    :items="items"
    :label="label"
    :loading="loading"
    :menu-props="{ maxHeight: '400' }"
    :search-input.sync="search"
    @update:search-input="fetchData({ q: $event })"
    item-text="name"
    item-value="id"
    v-model="individual"
  >
    <template v-slot:no-data>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title>
            No Indivduals matching "
            <strong>{{ search }}</strong
            >".
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </template>
  </v-combobox>
</template>

<script>
import { cloneDeep } from "lodash"

import SearchUtils from "@/search/utils"
import IndividualApi from "@/individual/api"

export default {
  name: "IndividualSelect",
  props: {
    value: {
      type: Object,
      default: function () {
        return {}
      },
    },
    label: {
      type: String,
      default: function () {
        return "Individual"
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
      search: null,
    }
  },

  computed: {
    individual: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.$emit("input", value)
      },
    },
  },

  created() {
    this.fetchData({})
  },

  methods: {
    fetchData() {
      this.error = null
      this.loading = "error"

      let filterOptions = {
        q: this.search,
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

      IndividualApi.getAll(filterOptions).then((response) => {
        this.items = response.data.items
        this.loading = false
      })
    },
  },
}
</script>
