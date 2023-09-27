<template>
  <v-autocomplete
    v-model="reference"
    :items="items"
    v-model:search="search"
    :menu-props="{ maxHeight: '400' }"
    item-title="name"
    :label="label"
    placeholder="Start typing to search"
    return-object
    :loading="loading"
    no-filter
    name="reference"
  >
    <template #append-inner>
      <v-btn icon variant="text" @click="createEditShow({})">
        <v-icon>mdi-plus</v-icon>
      </v-btn>
      <new-edit-sheet @new-document-created="addItem($event)" />
    </template>
  </v-autocomplete>
</template>

<script>
import { mapActions } from "vuex"
import { cloneDeep } from "lodash"

import DocumentApi from "@/document/api"
import NewEditSheet from "@/document/reference/TemplateNewEditSheet.vue"

export default {
  name: "TemplateSelect",

  props: {
    modelValue: {
      type: Object,
      default: function () {
        return {}
      },
    },
    resourceType: {
      type: String,
      default: "",
    },
    project: {
      type: [Object],
      default: null,
    },
    label: {
      type: String,
      default: "Template",
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
    reference: {
      get() {
        return cloneDeep(this.modelValue)
      },
      set(value) {
        this.$emit("update:modelValue", value)
      },
    },
  },

  methods: {
    ...mapActions("reference", ["createEditShow"]),
    addItem(value) {
      this.document = value
      this.items.push(value)
    },
    fetchData() {
      this.error = null
      this.loading = "error"
      let filterOptions = {
        q: this.search,
        sortBy: ["name"],
        itemsPerPage: this.itemsPerPage,
        filter: JSON.stringify({
          and: [
            {
              model: "Project",
              field: "name",
              op: "==",
              value: this.project.name,
            },
            {
              model: "Document",
              field: "resource_type",
              op: "==",
              value: this.resourceType,
            },
          ],
        }),
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
