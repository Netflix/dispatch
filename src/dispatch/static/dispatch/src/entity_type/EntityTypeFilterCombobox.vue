<template>
  <v-combobox
    :items="items"
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
    v-model="entity_types"
  >
    <template v-slot:no-data>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title>
            No entity types matching "
            <strong>{{ search }}</strong
            >"
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </template>
    <template v-slot:selection="{ item, index }">
      <v-chip close @click:close="entity_types.splice(index, 1)">
        <span v-if="item.entity_type"> {{ item.name }} </span>{{ item.name }}
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
    <template slot="append-outer">
      <entity-type-create-dialog
        v-model="createdEntityType"
        :project="project"
        :signalDefinition="signalDefinition"
      />
    </template>
  </v-combobox>
</template>

<script>
import { cloneDeep, debounce } from "lodash"

import SearchUtils from "@/search/utils"
import EntityTypeApi from "@/entity_type/api"
import EntityTypeCreateDialog from "@/entity_type/EntityTypeCreateDialog.vue"

export default {
  name: "EntityTypeFilterCombobox",

  props: {
    value: {
      type: Array,
      default: () => [],
    },
    label: {
      type: String,
      default: "Add Entity Types",
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
      required: true,
    },
    signalDefinition: {
      type: Object,
      required: true,
    },
  },

  components: { EntityTypeCreateDialog },

  data() {
    return {
      loading: false,
      items: [],
      more: false,
      numItems: 5,
      createdEntityType: null,
      search: null,
    }
  },

  computed: {
    entity_types: {
      get() {
        return this.value
      },
      set(value) {
        this.$emit("input", value)
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

      EntityTypeApi.getAll(filterOptions).then((response) => {
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
}
</script>
