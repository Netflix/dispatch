<template>
  <v-autocomplete
    v-model="document"
    :items="items"
    v-model:search="search"
    :menu-props="{ maxHeight: '400' }"
    item-title="name"
    label="Document"
    placeholder="Start typing to search"
    return-object
    :loading="loading"
    no-filter
    name="document"
  >
    <template #append>
      <v-btn icon variant="text" @click="createEditShow({})">
        <v-icon>mdi-plus</v-icon>
      </v-btn>
    </template>
  </v-autocomplete>
</template>

<script>
import { mapActions } from "vuex"
import { cloneDeep } from "lodash"

import SearchUtils from "@/search/utils"
import DocumentApi from "@/document/api"

export default {
  name: "DocumentSelect",

  props: {
    modelValue: {
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
      search: null,
      select: null,
      items: [],
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
    document: {
      get() {
        return cloneDeep(this.modelValue)
      },
      set(value) {
        this.$emit("update:modelValue", value)
      },
    },
  },

  methods: {
    ...mapActions("document", ["createEditShow"]),
    addItem(value) {
      this.document = value
      this.items.push(value)
    },
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

      DocumentApi.getAll(filterOptions).then((response) => {
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
