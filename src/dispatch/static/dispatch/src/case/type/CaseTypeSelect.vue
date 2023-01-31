<template>
  <v-combobox
    :items="items"
    :label="label"
    :loading="loading"
    :menu-props="{ maxHeight: '400' }"
    :search-input.sync="search"
    @update:search-input="getFilteredData({ q: $event })"
    item-text="name"
    item-value="id"
    v-model="case_type"
  >
    <template v-slot:no-data>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title>
            No case types matching
            <strong>"{{ search }}"</strong>
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </template>
    <template v-slot:item="data">
      <v-list-item-content>
        <v-list-item-title v-text="data.item.name" />
        <v-list-item-subtitle
          style="width: 200px"
          class="text-truncate"
          v-text="data.item.description"
        />
      </v-list-item-content>
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
import { cloneDeep, debounce } from "lodash"
import CaseTypeApi from "@/case/type/api"

export default {
  name: "CaseTypeSelect",

  props: {
    value: {
      type: Object,
      default: function () {
        return {}
      },
    },
    label: {
      type: String,
      default: "Type",
    },
  },

  data() {
    return {
      loading: false,
      items: [],
      numItems: 5,
      more: false,
      search: null,
    }
  },

  computed: {
    case_type: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.$emit("input", value)
      },
    },
  },

  methods: {
    loadMore() {
      this.numItems = this.numItems + 5
      this.fetchData()
    },
    fetchData() {
      this.error = null
      this.loading = "error"
      let filterOptions = {
        q: this.search,
        itemsPerPage: this.numItems,
        sortBy: ["name"],
        descending: [false],
      }

      CaseTypeApi.getAll(filterOptions).then((response) => {
        this.items = response.data.items

        // check to see if the current selection is available in the list and if not we add it
        if (!this.items.find((match) => match.id === this.case_type.id)) {
          this.items = [this.case_type].concat(this.items)
        }

        this.total = response.data.total

        if (this.items.length < this.total) {
          this.more = true
        } else {
          this.more = false
        }

        this.loading = false
      })
    },
    getFilteredData: debounce(function () {
      this.fetchData()
    }, 500),
  },

  created() {
    this.fetchData()
  },
}
</script>
