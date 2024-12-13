<template>
  <v-select
    v-model="selectedIncidentType"
    :items="items"
    :menu-props="{ maxHeight: '400' }"
    item-title="name"
    :label="label"
    return-object
    :loading="loading"
    :rules="[is_type_in_project]"
  >
    <template #item="{ props, item }">
      <v-list-item v-bind="props" :title="null">
        <v-list-item-title v-if="!project">
          {{ item.raw.project.display_name }}/{{ item.raw.name }}
        </v-list-item-title>
        <v-list-item-title v-else>
          {{ item.raw.name }}
        </v-list-item-title>
        <v-list-item-subtitle :title="item.raw.description">
          {{ item.raw.description }}
        </v-list-item-subtitle>
      </v-list-item>
    </template>
    <template #append-item>
      <v-list-item v-if="more" @click="loadMore">
        <v-list-item-subtitle>Load More</v-list-item-subtitle>
      </v-list-item>
    </template>
  </v-select>
</template>

<script>
import { debounce } from "lodash"
import SearchUtils from "@/search/utils"
import IncidentTypeApi from "@/incident/type/api"

export default {
  name: "IncidentTypeSelect",

  props: {
    modelValue: {
      type: Object,
      default: () => ({}),
    },
    project: {
      type: Object,
      default: null,
    },
    label: {
      type: String,
      default: () => "Type",
    },
  },

  data() {
    return {
      loading: false,
      items: [],
      more: false,
      numItems: 50,
      total: 0,
      lastProjectId: null,
      error: null,
      is_type_in_project: () => {
        this.validateType()
        return this.error
      },
    }
  },

  computed: {
    selectedIncidentType: {
      get() {
        if (!this.modelValue) return null
        if (this.modelValue.id) {
          return this.items.find((item) => item.id === this.modelValue.id) || null
        }
        // If we only have a name (e.g., from URL params), find by name
        if (this.modelValue.name) {
          return this.items.find((item) => item.name === this.modelValue.name) || null
        }
        return null
      },
      set(value) {
        this.$emit("update:modelValue", value)
        this.validateType()
      },
    },
  },

  watch: {
    project() {
      this.validateType()
      this.fetchData()
    },
  },

  methods: {
    validateType() {
      const project_id = this.project?.id || 0
      const in_project = this.selectedIncidentType?.project?.id == project_id
      if (in_project) {
        this.error = true
      } else {
        this.error = "Only types in selected project are allowed"
      }
    },
    clearSelection() {
      this.selectedIncidentType = null
    },
    loadMore() {
      this.numItems += 5
      this.fetchData()
    },
    fetchData: debounce(function () {
      this.loading = true

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
      }

      filterOptions.filters["enabled"] = ["true"]

      filterOptions = SearchUtils.createParametersFromTableOptions(
        { ...filterOptions },
        "IncidentType"
      )

      IncidentTypeApi.getAll(filterOptions)
        .then((response) => {
          this.items = response.data.items
          this.total = response.data.total
          this.more = this.items.length < this.total
        })
        .catch((error) => {
          console.error("Error fetching incident types:", error)
        })
        .finally(() => {
          this.loading = false
        })
    }, 300),
  },

  created() {
    this.fetchData()
  },
}
</script>
