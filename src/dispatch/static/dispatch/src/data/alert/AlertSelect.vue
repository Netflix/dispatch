<template>
  <v-autocomplete
    v-model="query"
    :items="items"
    item-title="name"
    :item-props="(item) => ({ subtitle: item.title })"
    v-model:search="search"
    :menu-props="{ maxHeight: '400' }"
    hide-selected
    :label="label"
    close
    clearable
    chips
    :loading="loading"
    return-object
    no-filter
  >
    <template #no-data>
      <v-list-item>
        <v-list-item-title>
          No querys matching "<strong>{{ search }}</strong
          >".
        </v-list-item-title>
      </v-list-item>
    </template>
  </v-autocomplete>
</template>

<script>
import QueryApi from "@/data/query/api"
import { cloneDeep } from "lodash"
export default {
  name: "QuerySelect",
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
        return "Query"
      },
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
    query: {
      get() {
        return cloneDeep(this.modelValue)
      },
      set(value) {
        this.$emit("update:modelValue", value)
      },
    },
  },

  watch: {
    search(val) {
      val && val !== this.select && this.querySelections(val)
    },
    value(val) {
      if (!val) return
      this.items.push(val)
    },
  },

  methods: {
    querySelections(v) {
      this.loading = "error"
      // Simulated ajax query
      QueryApi.getAll({ q: v }).then((response) => {
        this.items = response.data.items
        this.loading = false
      })
    },
  },

  created() {
    this.error = null
    this.loading = "error"
    QueryApi.getAll().then((response) => {
      this.items = response.data.items
      this.loading = false
    })
  },
}
</script>
