<template>
  <ValidationProvider name="template" immediate>
    <v-autocomplete
      v-model="template"
      :items="items"
      :search-input.sync="search"
      :menu-props="{ maxHeight: '400' }"
      slot-scope="{ errors, valid }"
      :error-messages="errors"
      :success="valid"
      item-text="name"
      :label="label"
      placeholder="Start typing to search"
      return-object
      :loading="loading"
      no-filter
    >
      <template slot="append-outer">
        <v-btn icon @click="createEditShow({})">
          <v-icon>add</v-icon>
        </v-btn>
        <new-edit-sheet @new-document-created="addItem($event)" />
      </template>
    </v-autocomplete>
  </ValidationProvider>
</template>

<script>
import { mapActions } from "vuex"
import { cloneDeep } from "lodash"
import { ValidationProvider } from "vee-validate"

import DocumentApi from "@/document/api"
import NewEditSheet from "@/document/template/TemplateNewEditSheet.vue"

export default {
  name: "TemplateSelect",

  props: {
    value: {
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
    ValidationProvider,
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
    template: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.$emit("input", value)
      },
    },
  },

  methods: {
    ...mapActions("template", ["createEditShow"]),
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
