<template>
  <v-combobox
    v-model="service"
    :items="items"
    v-model:search="search"
    :menu-props="{ maxHeight: '400' }"
    item-title="name"
    item-value="id"
    :label="label"
    placeholder="Start typing to search"
    return-object
    :hint="hint"
    :loading="loading"
    no-filter
  >
    <template #append>
      <v-btn icon variant="text" @click="createEditShow({})">
        <v-icon>mdi-plus</v-icon>
      </v-btn>
      <new-edit-sheet @new-service-created="addItem($event)" />
    </template>
  </v-combobox>
</template>

<script>
import { mapActions } from "vuex"
import { cloneDeep } from "lodash"

import SearchUtils from "@/search/utils"
import ServiceApi from "@/service/api"
import NewEditSheet from "@/service/NewEditSheet.vue"

export default {
  name: "ServiceSelect",

  props: {
    modelValue: {
      type: Object,
      default: function () {
        return {}
      },
    },
    label: {
      type: String,
      default: function () {
        return "Service"
      },
    },
    hint: {
      type: String,
      default: function () {
        return "Service to associate"
      },
    },
    project: {
      type: [Object],
      default: null,
    },
  },

  components: {
    NewEditSheet,
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
    service: {
      get() {
        return cloneDeep(this.modelValue)
      },
      set(value) {
        this.$emit("update:modelValue", value)
      },
    },
  },

  methods: {
    ...mapActions("service", ["createEditShow"]),
    addItem(v) {
      this.service = v
      this.items.push(v)
    },
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

      ServiceApi.getAll(filterOptions).then((response) => {
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
