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
    <template #selection="{ item, selected }">
      <v-menu origin="overlap">
        <template #activator="{ props }">
          <v-chip v-bind="props" :model-value="selected" pill closable @click:close="remove(item)">
            {{ item.name }}
          </v-chip>
        </template>
        <v-card>
          <v-list dark>
            <v-list-item>
              <v-list-item-avatar color="teal">
                <span class="text-white">{{ initials(item.name) }}</span>
              </v-list-item-avatar>

              <v-list-item-title>{{ item.name }}</v-list-item-title>
              <v-list-item-subtitle>{{ item.type }}</v-list-item-subtitle>

              <v-list-item-action>
                <v-btn icon variant="text">
                  <v-icon>mdi-close-circle</v-icon>
                </v-btn>
              </v-list-item-action>
            </v-list-item>
          </v-list>
          <v-list>
            <v-list-item>
              <v-list-item-action>
                <v-icon>mdi-text-box</v-icon>
              </v-list-item-action>
              <v-list-item-subtitle>{{ item.description }}</v-list-item-subtitle>
            </v-list-item>
            <v-list-item v-if="item.jpath">
              <v-list-item-action>
                <v-icon>mdi-code-json</v-icon>
              </v-list-item-action>
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
          No entity types matching "
          <strong>{{ search }}</strong
          >"
        </v-list-item-title>
      </v-list-item>
    </template>
    <template #item="data">
      <v-list-item-title> {{ data.item.name }} </v-list-item-title>
      <v-list-item-subtitle style="width: 200px" class="text-truncate">
        {{ data.item.description }}
      </v-list-item-subtitle>
    </template>
    <template #append-item>
      <v-list-item v-if="more" @click="loadMore()">
        <v-list-item-subtitle> Load More </v-list-item-subtitle>
      </v-list-item>
    </template>
    <template #append-outer>
      <entity-type-create-dialog
        v-model="createdEntityType"
        :project="project"
        :signalDefinition="signalDefinition"
      />
    </template>
  </v-combobox>
</template>

<script>
import { debounce } from "lodash"
import { initials } from "@/filters"

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

  setup() {
    return { initials }
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

  watch: {
    createdEntityType: function (newVal) {
      this.items.push(newVal)
      this.entity_types.push(newVal)
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
      }

      if (this.project) {
        filterOptions = {
          ...filterOptions,
          filters: {
            project: [this.project],
            scope: ["multiple"],
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
    remove(item) {
      this.entity_types.splice(this.entity_types.indexOf(item), 1)
    },
    getFilteredData: debounce(function () {
      this.fetchData()
    }, 500),
  },
}
</script>
