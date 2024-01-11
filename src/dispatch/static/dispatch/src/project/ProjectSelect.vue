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

export default {
  name: "ProjectSelect",

  props: {
    modelValue: {
      type: Object,
      default: function () {
        return {}
      },
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
        return cloneDeep(this.modelValue)
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
