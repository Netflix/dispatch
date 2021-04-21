<template>
  <v-combobox
    v-model="participant"
    :items="items"
    item-text="individual.name"
    :search-input.sync="search"
    hide-selected
    :label="label"
    clearable
    chips
    :loading="loading"
    @update:search-input="getFilteredData({ q: $event })"
    no-filter
    return-object
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
    <template v-slot:item="data">
      <v-list-item-content>
        <v-list-item-title v-text="data.item.individual.name" />
        <v-list-item-subtitle v-text="data.item.individual.email" />
      </v-list-item-content>
    </template>
    <template v-slot:selection="{ attr, on, item, selected }">
      <v-chip v-bind="attr" :input-value="selected" v-on="on">
        <span v-text="item.individual.name" />
      </v-chip>
    </template>
    <template v-slot:append-item>
      <v-list-item v-if="more" @click="loadMore()">
        <v-list-item-content>
          <v-list-item-subtitle> Load More </v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>
    </template>
  </v-combobox>
</template>

<script>
import IndividualApi from "@/individual/api"
import { cloneDeep, debounce } from "lodash"
export default {
  name: "ParticipantSelect",
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
        return "Participant"
      },
    },
  },

  data() {
    return {
      loading: false,
      items: [],
      more: false,
      numItems: 5,
      search: null,
    }
  },

  computed: {
    participant: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.$emit("input", value)
      },
    },
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
      this.loading = "error"
      IndividualApi.getAll(filterOptions).then((response) => {
        this.items = response.data.items.map(function (x) {
          return { individual: x }
        })
        this.total = response.data.total

        if (this.items.length < this.total) {
          this.more = true
        } else {
          this.more = false
        }

        this.loading = false
      })
    },
    getFilteredData: debounce(function (options) {
      this.fetchData(options)
    }, 500),
  },
}
</script>
