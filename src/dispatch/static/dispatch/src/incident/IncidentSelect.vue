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
    no-filter
  >
    <template v-slot:selection="{ attr, on, item, selected }">
      <v-chip v-bind="attr" :input-value="selected" v-on="on">
        <span v-text="item.name" />
      </v-chip>
    </template>
    <template v-slot:item="{ item }">
      <v-list-item-content>
        <v-list-item-title v-text="item.name" />
        <v-list-item-subtitle v-text="item.title" />
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
  name: "IncidentSelect",
  props: {
    value: {
      type: Object,
      default: function () {
        return null
      },
    },
    label: {
      type: String,
      default: function () {
        return "Incident"
      },
    },
  },

  data() {
    return {
      loading: false,
      items: [],
      search: null,
    }
  },

  computed: {
    incident: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.$emit("input", value)
      },
    },
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

  methods: {
    querySelections(v) {
      this.loading = "error"
      // Simulated ajax query
      IncidentApi.getAll({ q: v }).then((response) => {
        this.items = response.data.items
        this.loading = false
      })
    },
  },

  mounted() {
    this.error = null
    this.loading = "error"
    IncidentApi.getAll().then((response) => {
      this.items = response.data.items
      this.loading = false
    })
  },
}
</script>
