<template>
  <v-select
    v-model="incident_type"
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
      <v-list-item v-if="more" @click="loadMore()">
        <v-list-item-subtitle> Load More </v-list-item-subtitle>
      </v-list-item>
    </template>
  </v-select>
</template>

<script>
import { cloneDeep } from "lodash"

import SearchUtils from "@/search/utils"
import IncidentTypeApi from "@/incident/type/api"

export default {
  name: "IncidentTypeSelect",

  props: {
    modelValue: {
      type: Object,
      default: function () {
        return {}
      },
    },
    project: {
      type: [Object],
      default: null,
    },
    label: {
      type: String,
      default: function () {
        return "Type"
      },
    },
  },

  data() {
    return {
      loading: false,
      items: [],
      more: false,
      numItems: 5,
      error: null,
      is_type_in_project: () => {
        this.validateType()
        return this.error
      },
    }
  },

  computed: {
    incident_type: {
      get() {
        return cloneDeep(this.modelValue)
      },
      set(value) {
        this.$emit("update:modelValue", value)
        this.validateType()
      },
    },
  },

  methods: {
    loadMore() {
      this.numItems = this.numItems + 5
      this.fetchData()
    },
    validateType() {
      const project_id = this.project?.id || 0
      const in_project = this.incident_type?.project?.id == project_id
      if (in_project) {
        this.error = true
      } else {
        this.error = "Only types in selected project are allowed"
      }
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
            enabled: ["true"],
          },
        }
      }

      filterOptions = SearchUtils.createParametersFromTableOptions({ ...filterOptions })

      IncidentTypeApi.getAll(filterOptions).then((response) => {
        this.items = response.data.items

        this.total = response.data.total
        this.loading = false

        if (this.items.length < this.total) {
          this.more = true
        } else {
          this.more = false
        }
      })
    },
  },

  created() {
    this.fetchData()
    this.$watch(
      (vm) => [vm.project],
      () => {
        this.fetchData()
        this.validateType()
        this.$emit("update:modelValue", this.incident_type)
      }
    )
  },
}
</script>
