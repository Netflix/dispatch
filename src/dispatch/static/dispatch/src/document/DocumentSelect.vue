<template>
  <ValidationProvider name="document" immediate>
    <v-autocomplete
      v-model="document"
      :items="items"
      :search-input.sync="search"
      :menu-props="{ maxHeight: '400' }"
      slot-scope="{ errors, valid }"
      :error-messages="errors"
      :success="valid"
      item-text="name"
      label="Document"
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
import NewEditSheet from "@/document/NewEditSheet.vue"

export default {
  name: "DocumentSelect",

  props: {
    value: {
      type: Object,
      default: function () {
        return {}
      },
    },
    project: {
      type: String,
      default: null,
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
      val && val !== this.select && this.querySelections(val)
    },
    value(val) {
      if (!val) return
      this.items.push(val)
    },
  },

  computed: {
    document: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.$emit("input", value)
      },
    },
  },

  methods: {
    ...mapActions("document", ["createEditShow"]),
    addItem(value) {
      this.document = value
      this.items.push(value)
    },
    querySelections(v) {
      this.loading = "error"
      // Simulated ajax query
      DocumentApi.getAll({ q: v }).then((response) => {
        this.items = response.data.items
        this.loading = false
      })
    },
  },

  created() {
    this.error = null
    this.loading = "error"
    DocumentApi.getAll().then((response) => {
      this.items = response.data.items
      this.loading = false
    })
  },
}
</script>
