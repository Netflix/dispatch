<template>
  <v-container>
    <v-row no-gutter>
      <v-combobox
        :items="items"
        :label="label"
        :loading="loading"
        :menu-props="{ maxHeight: '400' }"
        v-model:search="search"
        @update:search="getFilteredData({ q: $event })"
        chips
        clearable
        close
        closable-chips
        hide-selected
        item-title="name"
        item-value="id"
        multiple
        no-filter
        v-model="filters"
      >
        <template #selection="{ item, selected }">
          <v-menu location="bottom right" transition="scale-transition" origin="top left">
            <template #activator="{ props }">
              <v-chip
                v-bind="props"
                :model-value="selected"
                pill
                closable
                @click:close="remove(item)"
              >
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
                <v-list-item v-if="item.expression">
                  <v-list-item-action>
                    <v-icon>mdi-code-json</v-icon>
                  </v-list-item-action>
                  <v-list-item-subtitle>
                    <pre>{{ item.expression }}</pre>
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-card>
          </v-menu>
        </template>
        <template #item="{ item }">
          <v-list-item-title>{{ item.name }}</v-list-item-title>
          <v-list-item-subtitle style="width: 200px" class="text-truncate">
            {{ item.description }}
          </v-list-item-subtitle>
        </template>
        <template #no-data>
          <v-list-item>
            <v-list-item-title>
              No filters matching "
              <strong>{{ search }}</strong>
            </v-list-item-title>
          </v-list-item>
        </template>
        <template #append-outer>
          <signal-filter-create-dialog
            v-model="createdFilter"
            :project="project"
            :signalDefinition="signalDefinition"
          />
        </template>
      </v-combobox>
    </v-row>
  </v-container>
</template>

<script>
import { cloneDeep, debounce } from "lodash"
import { initials } from "@/filters"

import SignalApi from "@/signal/api"
import SearchUtils from "@/search/utils"
import SignalFilterCreateDialog from "@/signal/filter/SignalFilterCreateDialog.vue"

export default {
  name: "SignalFilterCombobox",
  props: {
    value: {
      type: Array,
      default: function () {
        return []
      },
    },
    label: {
      type: String,
      default: "Signal Filters",
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

  components: { SignalFilterCreateDialog },

  data() {
    return {
      loading: false,
      items: [],
      search: null,
      createdFilter: null,
    }
  },

  setup() {
    return { initials }
  },

  computed: {
    filters: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.search = null
        const filters = value.filter((v) => {
          if (typeof v === "string") {
            return false
          }
          return true
        })
        this.$emit("input", filters)
      },
    },
  },

  watch: {
    createdFilter: function (newVal) {
      this.items.push(newVal)
      this.filters.push(newVal)
    },
  },

  methods: {
    remove(item) {
      this.filters.splice(this.filters.indexOf(item), 1)
    },
    fetchData() {
      this.error = null
      this.loading = "error"
      let filterOptions = {
        q: this.search,
        itemsPerPage: 50,
        sortBy: ["name"],
        descending: [false],
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

      SignalApi.getAllFilters(filterOptions).then((response) => {
        this.items = response.data.items
        this.loading = false
      })
    },
    getFilteredData: debounce(function (options) {
      this.fetchData(options)
    }, 500),
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
