<template>
  <v-select
    v-model="selectedIncidentType"
    :items="items"
    :menu-props="{ maxHeight: '400' }"
    item-title="name"
    :label="label"
    return-object
    :loading="loading"
    :rules="[validationRule]"
  >
    <template #item="{ props, item }">
      <v-list-item v-bind="props" :title="null">
        <v-list-item-title v-if="!project">
          {{ item.raw.project.name }}/{{ item.raw.name }}
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
      numItems: 5,
      total: 0,
      lastProjectId: null,
    }
  },

  computed: {
    selectedIncidentType: {
      get() {
        return this.modelValue || null
      },
      set(value) {
        this.$emit("update:modelValue", value)
      },
    },
    isTypeValid() {
      const project_id = this.project?.id || 0
      return this.selectedIncidentType?.project?.id == project_id
    },
    validationRule() {
      return this.isTypeValid || "Only types in selected project are allowed"
    },
  },

  watch: {
    project() {
      this.fetchData()
    },
  },

  methods: {
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
        filterOptions.filters = {
          project: [this.project],
          enabled: ["true"],
        }
      }

      filterOptions = SearchUtils.createParametersFromTableOptions(filterOptions)

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
