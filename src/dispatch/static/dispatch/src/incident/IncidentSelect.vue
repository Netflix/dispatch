<template>
  <v-autocomplete
    v-model="incident"
    :items="items"
    item-text="name"
    :search-input.sync="search"
    :menu-props="{ maxHeight: '400' }"
    hide-selected
    :label="label"
    close
    clearable
    :loading="loading"
    return-object
    cache-items
    :filter="customFilter"
  >
    <template v-slot:selection="{ attr, on, item, selected }">
      <v-chip v-bind="attr" :input-value="selected" v-on="on">
        <span v-text="item.name"></span>
      </v-chip>
    </template>
    <template v-slot:item="{ item }">
      <v-list-item-content>
        <v-list-item-title v-text="item.name"></v-list-item-title>
        <v-list-item-subtitle v-text="item.title"></v-list-item-subtitle>
      </v-list-item-content>
    </template>
    <template v-slot:no-data>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title>
            No incidents matching "
            <strong>{{ search }}</strong
            >".
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </template>
  </v-autocomplete>
</template>

<script>
import IncidentApi from "@/incident/api"
import { cloneDeep } from "lodash"
export default {
  name: "IncidentComboBox",
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
        return "Incident"
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
    incident: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.$emit("input", value)
      }
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

  methods: {
    querySelections(v) {
      this.loading = "error"
      // Simulated ajax query
      IncidentApi.getAll({ q: v }).then(response => {
        this.items = response.data.items
        this.loading = false
      })
    },
    customFilter(item, queryText) {
      const textOne = item.name.toLowerCase()
      const textTwo = item.title.toLowerCase()
      const textThree = item.description.toLowerCase()
      const searchText = queryText.toLowerCase()
      return (
        textOne.indexOf(searchText) > -1 ||
        textTwo.indexOf(searchText) > -1 ||
        textThree.indexOf(searchText) > -1
      )
    }
  },

  mounted() {
    this.error = null
    this.loading = "error"
    IncidentApi.getAll().then(response => {
      this.items = response.data.items
      this.loading = false
    })
  }
}
</script>
