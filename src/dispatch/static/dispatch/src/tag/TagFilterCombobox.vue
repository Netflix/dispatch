<template>
  <v-combobox
    v-model="tags"
    :items="items"
    item-text="name"
    :search-input.sync="search"
    hide-selected
    :label="label"
    multiple
    clearable
    chips
    :loading="loading"
    @update:search-input="getFilteredData({ q: $event })"
  >
    <template v-slot:no-data>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title>
            No Tags matching "
            <strong>{{ search }}</strong
            >"
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </template>
    <template v-slot:append-item>
      <v-list-item v-if="more" @click="loadMore()">
        <v-list-item-content>
          <v-list-item-subtitle>
            Load More
          </v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>
    </template>
  </v-combobox>
</template>

<script>
import TagApi from "@/tag/api"
import { cloneDeep, debounce } from "lodash"
export default {
  name: "TagCombobox",
  props: {
    value: {
      type: Array,
      default: function() {
        return []
      }
    },
    label: {
      type: String,
      default: "Add Tags"
    }
  },
  data() {
    return {
      loading: false,
      items: [],
      more: false,
      numItems: 5,
      search: null
    }
  },

  computed: {
    tags: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.search = null
        this._tags = value.map(v => {
          if (typeof v === "string") {
            v = {
              name: v
            }
            this.items.push(v)
          }
          return v
        })
        this.$emit("input", this._tags)
      }
    }
  },

  created() {
    this.fetchData({})
  },

  methods: {
    loadMore() {
      this.numItems = this.numItems + 5
      this.getFilteredData({ q: this.search, itemsPerPage: this.numItems })
    },
    fetchData(filterOptions) {
      this.error = null
      this.loading = true
      TagApi.getAll(filterOptions).then(response => {
        this.items = response.data.items
        this.total = response.data.total

        if (this.items.length < this.total) {
          this.more = true
        } else {
          this.more = false
        }

        this.loading = false
      })
    },
    getFilteredData: debounce(function(options) {
      this.fetchData(options)
    }, 500)
  }
}
</script>
