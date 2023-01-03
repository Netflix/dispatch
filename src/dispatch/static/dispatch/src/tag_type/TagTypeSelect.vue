<template>
  <v-select
    v-model="tag_type"
    :items="items"
    :menu-props="{ maxHeight: '400' }"
    item-text="name"
    label="Type"
    return-object
    :loading="loading"
  >
    <template v-slot:item="data">
      <template>
        <v-list-item-content>
          <v-list-item-title v-text="data.item.name" />
          <v-list-item-subtitle
            style="width: 200px"
            class="text-truncate"
            v-text="data.item.description"
          />
        </v-list-item-content>
      </template>
    </template>
    <template v-slot:append-item>
      <v-list-item v-if="more" @click="loadMore()">
        <v-list-item-content>
          <v-list-item-subtitle> Load More </v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>
    </template>
  </v-select>
</template>

<script>
import { cloneDeep } from "lodash"

import SearchUtils from "@/search/utils"
import TagTypeApi from "@/tag_type/api"

export default {
  name: "TagTypeSelect",

  props: {
    value: {
      type: Object,
      default: function () {
        return {}
      },
    },
    project: {
      type: [Object],
      default: null,
    },
  },

  data() {
    return {
      loading: false,
      items: [],
      more: false,
      numItems: 5,
    }
  },

  computed: {
    tag_type: {
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

      TagTypeApi.getAll(filterOptions).then((response) => {
        this.items = response.data.items

        // check to see if the current selection is available in the list and if not we add it
        if (!this.items.find((match) => match.id === this.tag_type.id)) {
          this.items = [this.tag_type].concat(this.items)
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
  },

  created() {
    this.fetchData()
    this.$watch(
      (vm) => [vm.project],
      () => {
        this.fetchData()
      }
    )
  },
}
</script>
