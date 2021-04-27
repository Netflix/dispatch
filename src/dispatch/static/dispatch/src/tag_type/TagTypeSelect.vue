<template>
  <v-select
    v-model="tag_type"
    :items="items"
    :menu-props="{ maxHeight: '400' }"
    item-text="name"
    label="Type"
    return-object
    :loading="loading"
  >
    <template v-slot:item="data">
      <template>
        <v-list-item-content>
          <v-list-item-title v-text="data.item.name" />
          <v-list-item-subtitle
            style="width: 200px"
            class="text-truncate"
            v-text="data.item.description"
          />
        </v-list-item-content>
      </template>
    </template>
  </v-select>
</template>

<script>
import { cloneDeep } from "lodash"

import SearchUtils from "@/search/utils"
import TagTypeApi from "@/tag_type/api"

export default {
  name: "TagTypeSelect",

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
    tag_type: {
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
      this.loading = "error"
      let filterOptions = {
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
      TagTypeApi.getAll(filterOptions).then((response) => {
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
