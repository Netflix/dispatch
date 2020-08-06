<template>
  <v-autocomplete
    v-model="assignee"
    :items="items"
    :search-input.sync="search"
    :menu-props="{ maxHeight: '400' }"
    hide-selected
    :label="label"
    item-text="name"
    multiple
    close
    chips
    clearable
    return-object
    placeholder="Start typing to search"
    cache-items
    :loading="loading"
  >
    <template v-slot:no-data>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title>
            No individuals matching "
            <strong>{{ search }}</strong
            >".
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </template>
  </v-autocomplete>
</template>

<script>
import IndividualApi from "@/individual/api"
import { map } from "lodash"
export default {
  name: "AssigneeComboBox",
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
        return "Assignee"
      }
    }
  },

  data() {
    return {
      loading: false,
      items: [],
      select: null,
      search: null
    }
  },

  computed: {
    assignee: {
      get() {
        return map(this.value, function(item) {
          return item["individual"]
        })
      },
      set(value) {
        let wrapped = map(value, function(item) {
          if (!("individual" in item)) {
            return { individual: item }
          }
          return item
        })
        this.$emit("input", wrapped)
      }
    }
  },

  watch: {
    search(val) {
      val && val !== this.select && this.querySelections(val)
    },
    value(val) {
      if (!val) return
      this.items.push.apply(
        this.items,
        map(val, function(item) {
          return item["individual"]
        })
      )
    }
  },

  methods: {
    querySelections(v) {
      this.loading = true
      // Simulated ajax query
      IndividualApi.getAll({ q: v }).then(response => {
        this.items = response.data.items
        this.loading = false
      })
    }
  },

  mounted() {
    this.error = null
    this.loading = true
    IndividualApi.getAll().then(response => {
      this.items = response.data.items
      this.loading = false
    })
  }
}
</script>
