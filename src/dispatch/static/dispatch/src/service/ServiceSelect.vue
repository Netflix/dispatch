<template>
  <v-autocomplete
    v-model="service"
    :items="items"
    :search-input.sync="search"
    :menu-props="{ maxHeight: '400' }"
    cache-items
    item-text="name"
    label="Service"
    placeholder="Start typing to Search"
    return-object
    :loading="loading"
  />
</template>

<script>
import ServiceApi from "@/service/api"
import _ from "lodash"
export default {
  name: "ServiceSelect",

  props: {
    value: {
      type: Object,
      default: function() {
        return {}
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
    }
  },

  computed: {
    service: {
      get() {
        return _.cloneDeep(this.value)
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

  created() {
    this.error = null
    this.loading = true
    ServiceApi.getAll().then(response => {
      this.items = response.data.items
      this.loading = false
    })
  }
}
</script>
