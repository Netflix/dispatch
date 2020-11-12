<template>
  <v-autocomplete
    v-model="service"
    :items="items"
    :search-input.sync="search"
    :menu-props="{ maxHeight: '400' }"
    cache-items
    item-text="name"
    :label="label"
    placeholder="Start typing to Search"
    return-object
    :hint="hint"
    :loading="loading"
  />
</template>

<script>
import ServiceApi from "@/service/api"
import { cloneDeep } from "lodash"
export default {
  name: "ServiceSelect",

  props: {
    value: {
      type: Object,
      default: function() {
        return {}
      }
    },
    label: {
      type: String,
      default: function() {
        return "Service"
      }
    },
    hint: {
      type: String,
      default: function() {
        return "Service to associate"
      }
    }
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
    service: {
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
      ServiceApi.getAll({ q: v }).then(response => {
        this.items = response.data.items
        this.loading = false
      })
    }
  },

  mounted() {
    this.error = null
    this.loading = true
    ServiceApi.getAll().then(response => {
      this.items = response.data.items
      this.loading = false
    })
  }
}
</script>
