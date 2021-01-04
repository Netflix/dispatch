<template>
  <v-autocomplete
    v-model="participant"
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
        <span v-text="item.individual.name"></span>
      </v-chip>
    </template>
    <template v-slot:item="{ item }">
      <v-list-item-content>
        <v-list-item-title v-text="item.individual.name"></v-list-item-title>
        <v-list-item-subtitle v-text="item.individual.email"></v-list-item-subtitle>
      </v-list-item-content>
    </template>
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
import { cloneDeep } from "lodash"
export default {
  name: "ParticipantSelect",
  props: {
    value: {
      type: Object,
      default: function() {
        return null
      }
    },
    label: {
      type: String,
      default: function() {
        return "Participant"
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
    participant: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.$emit("input", value)
      }
    }
  },

  mounted() {
    this.fetchData({})
  },

  watch: {
    search(val) {
      if (!val) {
        return
      }
      this.getFilteredData({ q: val })
    },
    value(val) {
      if (!val) return
      this.items.push(val)
    }
  },

  methods: {
    fetchData(filterOptions) {
      this.loading = "error"
      IndividualApi.getAll(filterOptions).then(response => {
        this.items = response.data.items.map(function(x) {
          return { individual: x }
        })
        this.loading = false
      })
    },
    getFilteredData(query) {
      // cancel pending call
      clearTimeout(this._timerId)

      // delay new call 500ms
      this._timerId = setTimeout(() => {
        this.fetchData(query)
      }, 500)
    }
  }
}
</script>
