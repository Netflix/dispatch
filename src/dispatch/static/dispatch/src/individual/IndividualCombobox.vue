<template>
  <v-combobox
    v-model="individual"
    :items="items"
    item-text="name"
    :search-input.sync="search"
    :menu-props="{ maxHeight: '400' }"
    hide-selected
    :label="label"
    multiple
    close
    chips
    clearable
    :loading="loading"
    @update:search-input="fetchData({ q: $event })"
  >
    <template v-slot:no-data>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title>
            No Indivduals matching "
            <strong>{{ search }}</strong
            >".
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </template>
  </v-combobox>
</template>

<script>
import IndividualApi from "@/individual/api"
import { cloneDeep, debounce } from "lodash"
export default {
  name: "IndividualComboBox",
  props: {
    value: {
      type: Array,
      default: function() {
        return []
      }
    },
    label: {
      type: String,
      default: function() {
        return "Individual"
      }
    }
  },

  data() {
    return {
      loading: false,
      items: [],
      search: null
    }
  },

  computed: {
    individual: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.search = null
        this._individuals = value.map(v => {
          if (typeof v === "string") {
            v = {
              name: v
            }
            this.items.push(v)
          }
          return v
        })
        this.$emit("input", this._individuals)
      }
    }
  },

  created() {
    this.fetchData({})
  },

  methods: {
    fetchData(filterOptions) {
      this.error = null
      this.loading = true
      IndividualApi.getAll(filterOptions).then(response => {
        this.items = response.data.items
        this.loading = false
      })
    },
    getFilteredData: debounce(function(options) {
      this.fetchData(options)
    }, 500)
  }
}
</script>
