<template>
  <v-combobox
    :items="items"
    :label="label"
    :loading="loading"
    v-model:search="search"
    @update:search="getFilteredData()"
    chips
    clearable
    closable-chips
    hide-selected
    item-title="name"
    item-value="id"
    multiple
    no-filter
    v-model="entity_types"
  >
    <template #chip="{ item, props }">
      <v-menu origin="overlap">
        <template #activator="{ props: menuProps }">
          <v-chip v-bind="mergeProps(props, menuProps)" pill />
        </template>
        <v-card>
          <v-list dark>
            <v-list-item>
              <template #prepend>
                <v-avatar color="teal">
                  <span class="text-white">{{ initials(item.name) }}</span>
                </v-avatar>
              </template>

              <v-list-item-title>{{ item.name }}</v-list-item-title>
              <v-list-item-subtitle>{{ item.type }}</v-list-item-subtitle>

              <template #append>
                <v-btn icon variant="text">
                  <v-icon>mdi-close-circle</v-icon>
                </v-btn>
              </template>
            </v-list-item>
          </v-list>
          <v-list>
            <v-list-item>
              <template #prepend>
                <v-icon>mdi-text-box</v-icon>
              </template>

              <v-list-item-subtitle>{{ item.description }}</v-list-item-subtitle>
            </v-list-item>
            <v-list-item v-if="item.jpath">
              <template #prepend>
                <v-icon>mdi-code-json</v-icon>
              </template>

              <v-list-item-subtitle>
                <pre>{{ item.jpath }}</pre>
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-card>
      </v-menu>
    </template>
    <template #no-data>
      <v-list-item>
        <v-list-item-title>
          No entity types matching "<strong>{{ search }}</strong
          >"
        </v-list-item-title>
      </v-list-item>
    </template>
    <template #item="data">
      <v-list-item v-bind="data.props" :title="null">
        <v-list-item-title> {{ data.item.raw.name }} </v-list-item-title>
        <v-list-item-subtitle :title="data.item.raw.description">
          {{ data.item.raw.description }}
        </v-list-item-subtitle>
      </v-list-item>
    </template>
    <template #append-item>
      <v-list-item v-if="more" @click="loadMore()">
        <v-list-item-subtitle> Load More </v-list-item-subtitle>
      </v-list-item>
    </template>
    <template #append>
      <entity-type-create-dialog
        @create="createEntityType"
        :project="project"
        :signalDefinition="signalDefinition"
      />
    </template>
  </v-combobox>
</template>

<script>
import { debounce } from "lodash"
import { initials } from "@/filters"
import { mergeProps } from "vue"

import SearchUtils from "@/search/utils"
import EntityTypeApi from "@/entity_type/api"
import EntityTypeCreateDialog from "@/entity_type/EntityTypeCreateDialog.vue"

export default {
  name: "EntityTypeFilterCombobox",

  props: {
    modelValue: {
      type: Array,
      default: () => [],
    },
    label: {
      type: String,
      default: "Add Entity Type Filters",
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
      search: null,
    }
  },

  setup() {
    return { initials, mergeProps }
  },

  computed: {
    entity_types: {
      get() {
        return this.modelValue
      },
      set(value) {
        this.$emit("update:modelValue", value)
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
    createEntityType(value) {
      this.items.push(value)
      this.entity_types.push(value)
    },
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
            scope: ["multiple", "single"],
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
