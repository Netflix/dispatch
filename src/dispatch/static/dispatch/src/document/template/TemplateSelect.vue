<template>
  <ValidationProvider name="template" immediate>
    <v-combobox
      v-model="template"
      :items="items"
      :search-input.sync="search"
      :menu-props="{ maxHeight: '400' }"
      item-text="name"
      item-value="id"
      :label="label"
      placeholder="Start typing to search"
      return-object
      :hint="hint"
      :loading="loading"
      no-filter
    >
      <template slot="append-outer">
        <v-btn icon @click="createEditShow({ resource_type: resourceType })">
          <v-icon>add</v-icon>
        </v-btn>
        <new-edit-sheet @new-document-created="addItem($event)" />
      </template>
      <template v-slot:no-data>
        <v-list-item>
          <v-list-item-content>
            <v-list-item-title>
              No results matching "<strong>{{ search }}</strong
              >"
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </template>
      <template v-slot:append-item>
        <v-list-item v-if="more" @click="loadMore()">
          <v-list-item-content>
            <v-list-item-subtitle> Load More </v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
      </template>
    </v-combobox>
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
    hint: {
      type: String,
      default: function () {
        return "Template to associate"
      },
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
      more: false,
      numItems: 5,
    }
  },

  watch: {
    search() {
      this.fetchData()
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

        // check to see if the current selection is available in the list and if not we add it
        if (!this.items.find((match) => match.id === this.template.id)) {
          this.items = [this.template].concat(this.items)
        }

        this.total = response.data.total

        if (this.items.length < this.total) {
          this.more = true
        } else {
          this.more = false
        }

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
