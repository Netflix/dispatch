<template>
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
    v-model="signalDefinitions"
  >
    <template #chip="{ item, props }">
      <v-menu v-model="menu" origin="overlap">
        <template #activator="{ props: menuProps }">
          <v-chip v-bind="mergeProps(props, menuProps)" pill />
        </template>
        <v-card>
          <v-list dark>
            <v-list-item>
              <template #prepend>
                <v-avatar color="teal">
                  {{ initials(item.name) }}
                </v-avatar>
              </template>

              <v-list-item-title>{{ item.name }}</v-list-item-title>
              <v-list-item-subtitle>{{ item.type }}</v-list-item-subtitle>

              <template #append>
                <v-btn icon variant="text" @click="menu = false">
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
          </v-list>
        </v-card>
      </v-menu>
    </template>
    <template #item="{ props, item }">
      <v-list-item v-bind="props" :title="null">
        <v-list-item-title>{{ item.raw.name }}</v-list-item-title>
        <v-list-item-subtitle :title="item.raw.description">
          {{ item.raw.description }}
        </v-list-item-subtitle>
      </v-list-item>
    </template>
    <template #no-data>
      <v-list-item>
        <v-list-item-title>
          No signal definition matching "
          <strong>{{ search }}</strong>
        </v-list-item-title>
      </v-list-item>
    </template>
  </v-combobox>
</template>

<script>
import { cloneDeep, debounce } from "lodash"
import { initials } from "@/filters"
import { mergeProps } from "vue"

import SignalApi from "@/signal/api"
import SearchUtils from "@/search/utils"

export default {
  name: "SignalDefinitionCombobox",
  props: {
    modelValue: {
      type: Array,
      default: function () {
        return []
      },
    },
    label: {
      type: String,
      default: "Signal Definitions",
    },
    project: {
      type: [Object],
      default: null,
    },
    defaultSignals: {
      type: [Object],
      default: null,
    },
  },

  data() {
    return {
      loading: false,
      items: [],
      search: null,
      createdFilter: null,
      menu: false,
    }
  },

  setup() {
    return { initials, mergeProps }
  },

  computed: {
    signalDefinitions: {
      get() {
        return cloneDeep(this.modelValue)
      },
      set(value) {
        this.search = null
        const signalDefinitions = value.filter((v) => {
          if (typeof v === "string") {
            return false
          }
          return true
        })
        this.$emit("update:modelValue", signalDefinitions)
      },
    },
  },

  methods: {
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

      SignalApi.getAll(filterOptions).then((response) => {
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
    if (this.defaultSignal) {
      this.filters = [this.defaultSignal]
    }
    this.$watch(
      (vm) => [vm.project],
      () => {
        this.fetchData()
      }
    )
  },
}
</script>
