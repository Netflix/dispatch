<template>
  <v-combobox
    :items="items"
    :label="label"
    :loading="loading"
    v-model:search="search"
    @update:search="getFilteredData()"
    chips
    closable-chips
    clearable
    hide-selected
    item-title="name"
    item-value="id"
    multiple
    no-filter
    v-model="tags"
    :menu-props="{ maxWidth: 0 }"
  >
    <template #no-data>
      <v-list-item>
        <v-list-item-title>
          No tags matching "
          <strong>{{ search }}</strong
          >"
        </v-list-item-title>
      </v-list-item>
    </template>
    <template #chip="{ item, props }">
      <v-chip v-bind="props">
        <span v-if="item.raw.tag_type"> {{ item.raw.project.name }}/ </span>{{ item.raw.name }}
      </v-chip>
    </template>
    <template #item="{ props, item }">
      <v-list-item v-bind="props" :title="null">
        <v-list-item-title> {{ item.raw.project.name }}/{{ item.raw.name }} </v-list-item-title>
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
import TagTypeApi from "@/tag_type/api"

export default {
  name: "TagTypeCombobox",

  props: {
    modelValue: {
      type: Array,
      default: function () {
        return []
      },
    },
    label: {
      type: String,
      default: "Add Tag Types",
    },
    model: {
      type: String,
      default: null,
    },
    modelId: {
      type: Number,
      default: null,
    },
    project: {
      type: Object,
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
    tags: {
      get() {
        return cloneDeep(this.modelValue)
      },
      set(value) {
        this.search = null
        const tags = value.filter((v) => {
          if (typeof v === "string") {
            return false
          }
          return true
        })
        this.$emit("update:modelValue", tags)
      },
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
