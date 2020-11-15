<template>
  <ValidationProvider name="document" immediate>
    <v-autocomplete
      v-model="document"
      :items="items"
      :search-input.sync="search"
      :menu-props="{ maxHeight: '400' }"
      cache-items
      slot-scope="{ errors, valid }"
      :error-messages="errors"
      :success="valid"
      item-text="name"
      label="Document"
      placeholder="Start typing to search"
      return-object
      :loading="loading"
    />
  </ValidationProvider>
</template>

<script>
import DocumentApi from "@/document/api"
import { cloneDeep } from "lodash"
import { ValidationProvider } from "vee-validate"
export default {
  name: "DocumentSelect",

  props: {
    value: {
      type: Object,
      default: function() {
        return {}
      }
    }
  },

  components: {
    ValidationProvider
  },

  data() {
    return {
      loading: false,
      search: null,
      select: null,
      items: []
    }
  },

  watch: {
    search(val) {
      val && val !== this.select && this.querySelections(val)
    },
    value(val) {
      if (!val) return
      this.items.push(val)
    }
  },

  computed: {
    document: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.$emit("input", value)
      }
    }
  },

  methods: {
    querySelections(v) {
      this.loading = true
      // Simulated ajax query
      DocumentApi.getAll({ q: v }).then(response => {
        this.items = response.data.items
        this.loading = false
      })
    }
  },

  mounted() {
    this.error = null
    this.loading = true
    DocumentApi.getAll().then(response => {
      this.items = response.data.items
      this.loading = false
    })
  }
}
</script>
