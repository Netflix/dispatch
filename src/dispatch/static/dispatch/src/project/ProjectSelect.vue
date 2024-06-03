<template>
  <v-select
    :items="items"
    :label="label"
    :loading="loading"
    :menu-props="{ maxHeight: '400' }"
    item-title="name"
    item-value="id"
    v-model="project"
    return-object
  >
    <template #no-data>
      <v-list-item>
        <v-list-item-title>
          No projects matching
          <strong>"{{ search }}"</strong>
        </v-list-item-title>
      </v-list-item>
    </template>
    <template #item="data">
      <v-list-item v-bind="data.props" :title="null">
        <v-list-item-title>{{ data.item.raw.name }}</v-list-item-title>
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
  </v-select>
</template>

<script>
import { cloneDeep, debounce } from "lodash"
import ProjectApi from "@/project/api"
import SearchUtils from "@/search/utils"

export default {
  name: "ProjectSelect",

  props: {
    modelValue: {
      type: Object,
      default: function () {
        return {}
      },
    },
    excludeDisabled: {
      type: Boolean,
      default: false,
    },
    label: {
      type: String,
      default: "Project",
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
    project: {
      get() {
        let projects = cloneDeep(this.modelValue)
        if (this.excludeDisabled && projects && Array.isArray(projects) && projects.length > 0) {
          projects = projects.filter((project) => {
            return project.enabled
          })
        }
        return projects
      },
      set(value) {
        this.$emit("update:modelValue", value)
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
        q: "",
        itemsPerPage: this.numItems,
        sortBy: ["name"],
        descending: [false],
      }

      if (this.excludeDisabled) {
        filterOptions = {
          filters: {
            enabled: [true],
          },
          ...filterOptions,
        }
      }

      filterOptions = SearchUtils.createParametersFromTableOptions({ ...filterOptions })

      ProjectApi.getAll(filterOptions).then((response) => {
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

  created() {
    this.fetchData()
  },
}
</script>
