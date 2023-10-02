<template>
  <v-autocomplete
    v-if="currentUser().experimental_features"
    :items="items"
    :label="label"
    :loading="loading"
    :filter="customFilter"
    :search-input.sync="search"
    chips
    clearable
    deletable-chips
    hide-selected
    item-text="individual.name"
    item-value="individual"
    return-object
    cache-items
    v-model="participant"
  >
    <template #no-data>
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
    <template #item="data">
      <v-list-item-content>
        <v-list-item-title>👤 {{ data.item.individual.name }}</v-list-item-title>
        <v-list-item-subtitle>{{ data.item.individual.email }}</v-list-item-subtitle>
      </v-list-item-content>
    </template>
    <template #selection="{ attr, on, item, selected }">
      <v-chip v-bind="attr" :input-value="selected" v-on="on">
        <span v-text="item.individual.name" />
      </v-chip>
    </template>
  </v-autocomplete>
  <v-combobox
    v-else
    :items="items"
    :label="label"
    :loading="loading"
    :search-input.sync="search"
    @update:search-input="getFilteredData()"
    chips
    clearable
    deletable-chips
    hide-selected
    item-text="individual.name"
    no-filter
    return-object
    v-model="participant"
  >
    <template #no-data>
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
    <template #item="data">
      <v-list-item-content>
        <v-list-item-title>{{ data.item.individual.name }}</v-list-item-title>
        <v-list-item-subtitle>{{ data.item.individual.email }}</v-list-item-subtitle>
      </v-list-item-content>
    </template>
    <template #selection="{ attr, on, item, selected }">
      <v-chip v-bind="attr" :input-value="selected" v-on="on">
        <span v-text="item.individual.name" />
      </v-chip>
    </template>
    <template #append-item>
      <v-list-item v-if="more" @click="loadMore()">
        <v-list-item-content>
          <v-list-item-subtitle> Load More </v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>
    </template>
  </v-combobox>
</template>

<script>
import { cloneDeep, debounce } from "lodash"
import { mapState } from "vuex"
import UserApi from "@/auth/api"

import SearchUtils from "@/search/utils"
import IndividualApi from "@/individual/api"

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
      experimental_features: false,
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
    UserApi.getUserInfo()
      .then((response) => {
        this.experimental_features = response.data.experimental_features
        if (this.experimental_features) {
          this.fetchDataExperimental()
        } else {
          this.fetchData()
        }
      })
      .catch((error) => {
        console.error("Error occurred while updating experimental features: ", error)
        this.fetchData()
      })
  },

  methods: {
    ...mapState("auth", ["currentUser"]),
    customFilter(item, queryText) {
      const name = item.individual.name.toLowerCase()
      const email = item.individual.email.toLowerCase()
      const searchText = queryText.toLowerCase()

      return name.indexOf(searchText) > -1 || email.indexOf(searchText) > -1
    },
    loadMore() {
      this.numItems = this.numItems + 5
      this.fetchData()
    },
    fetchDataExperimental() {
      this.loading = "error"
      let filterOptions = {
        q: this.search,
        sortBy: ["name"],
        descending: [false],
        itemsPerPage: -1,
      }

      if (this.project) {
        filterOptions = {
          ...filterOptions,
          filters: {
            project: [this.project],
          },
        }
        filterOptions = SearchUtils.createParametersFromTableOptions({ ...filterOptions })
      }

      IndividualApi.getAll(filterOptions).then((response) => {
        this.items = response.data.items.map(function (x) {
          return { individual: x }
        })
        this.loading = false
      })
    },
    fetchData() {
      this.loading = "error"
      let filterOptions = {
        q: this.search,
        sortBy: ["name"],
        descending: [false],
        itemsPerPage: this.numItems,
      }

      if (this.project) {
        filterOptions = {
          ...filterOptions,
          filters: {
            project: [this.project],
          },
        }
        filterOptions = SearchUtils.createParametersFromTableOptions({ ...filterOptions })
      }

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

    getFilteredDataExperimental: debounce(function () {
      this.fetchDataExperimental()
    }, 500),
    getFilteredData: debounce(function () {
      this.fetchData()
    }, 500),
  },
}
</script>
