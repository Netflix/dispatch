<template>
  <v-combobox
    :items="items | filterGlobal"
    :label="label"
    :loading="loading"
    :search-input.sync="search"
    @update:search-input="getFilteredData()"
    chips
    clearable
    hide-selected
    item-text="name"
    item-value="id"
    multiple
    no-filter
    v-model="entities"
  >
    <template v-slot:no-data>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title>
            No entities matching "
            <strong>{{ search }}</strong
            >"
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </template>
    <template v-slot:selection="{ item, index }">
      <v-chip close @click:close="value.splice(index, 1)">
        <span v-if="item.entity"> {{ item.name }} </span>
      </v-chip>
    </template>
    <template v-slot:item="data">
      <v-list-item-content>
        <v-list-item-title> {{ data.item.name }} </v-list-item-title>
        <v-list-item-subtitle style="width: 200px" class="text-truncate">
          {{ data.item.regular_expression }}
        </v-list-item-subtitle>
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

import SearchUtils from "@/search/utils"
import EntitiesApi from "@/entities/api"

export default {
  name: "EntityCombobox",

  props: {
    value: {
      type: Array,
      default: function () {
        return []
      },
    },
    label: {
      type: String,
      default: "Add Entities",
    },
    model: {
      type: String,
      default: null,
    },
    modelId: {
      type: Number,
      default: null,
    },
    project: {
      type: Object,
      default: null,
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
    entities: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.search = null
        this._entities = value.filter((v) => {
          if (typeof v === "string") {
            return false
          }
          return true
        })
        this.$emit("input", this._entities)
      },
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

      EntitiesApi.getAll(filterOptions).then((response) => {
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
    getFilteredData: debounce(function () {
      this.fetchData()
    }, 500),
  },

  filters: {
    filterGlobal: function(entities) {
      return entities.filter(entity => entity.global_find === false);
    }
  }
}
</script>
