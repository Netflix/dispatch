<template>
  <v-select
    v-model="selectedCaseType"
    :items="items"
    :menu-props="{ maxHeight: '400' }"
    item-title="name"
    item-value="id"
    :label="label"
    :hint="hint"
    return-object
    :loading="loading"
    no-filter
    :error-messages="show_error"
    :rules="[isTypeInProject]"
    clearable
  >
    <template #item="data">
      <v-list-subheader dense class="custom-subheader" v-if="data.item.raw.category">
        {{ data.item.raw.category }}
      </v-list-subheader>
      <v-list-item v-bind="data.props" :title="null" v-if="!data.item.raw.category">
        <v-list-item-title>{{ data.item.raw.name }}</v-list-item-title>
        <v-list-item-subtitle class="truncate-text" :title="data.item.raw.description">
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
import SearchUtils from "@/search/utils"
import CaseTypeApi from "@/case/type/api"

export default {
  name: "CaseTypeSelect",

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
    hint: {
      type: String,
      default: () => "Case Type to associate",
    },
  },

  data() {
    return {
      loading: false,
      items: [],
      more: false,
      numItems: 40,
      error: null,
      lastProjectId: null,
      isTypeInProject: () => {
        this.validateType()
        return this.error
      },
    }
  },

  computed: {
    selectedCaseType: {
      get() {
        if (!this.modelValue) return null
        if (this.modelValue.id) {
          return this.items.find((item) => item.id === this.modelValue.id) || null
        }
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
    show_error() {
      return null // Implement any specific error logic here if needed
    },
  },

  methods: {
    loadMore() {
      this.numItems += 40
      this.fetchData()
    },
    validateType() {
      const project_id = this.project?.id || 0
      const in_project = this.selectedCaseType?.project?.id == project_id
      if (in_project) {
        this.error = true
      } else {
        this.error = "Only types in selected project are allowed"
      }
    },
    fetchData() {
      this.error = null
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
            enabled: ["true"],
          },
        }
      }

      filterOptions = SearchUtils.createParametersFromTableOptions({ ...filterOptions })

      CaseTypeApi.getAll(filterOptions)
        .then((response) => {
          this.items = []
          let new_items = {}
          response.data.items.forEach((item) => {
            let category = "Team: " + (item.oncall_service?.name || "None")
            new_items[category] = new_items[category] || []
            new_items[category].push(item)
          })
          let keys = Object.keys(new_items)
          keys.sort((a, b) => {
            if (a === "Team: None") return 1
            if (b === "Team: None") return -1
            return a.localeCompare(b)
          })
          keys.forEach((category) => {
            this.items.push({ category: category })
            for (let item of new_items[category]) {
              this.items.push(item)
            }
          })
          this.more = response.data.total > this.items.length
        })
        .catch((error) => {
          console.error("Error fetching case types:", error)
          this.error = "Failed to load case types"
        })
        .finally(() => {
          this.loading = false
        })
    },
    resetSelection() {
      this.$emit("update:modelValue", null)
    },
  },

  watch: {
    project: {
      handler(newProject) {
        if (newProject?.id !== this.lastProjectId) {
          this.lastProjectId = newProject?.id
          this.resetSelection()
          this.fetchData()
        }
        this.validateType()
      },
      deep: true,
    },
  },

  created() {
    this.fetchData()
  },
}
</script>

<style scoped>
.truncate-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 500px;
}
.custom-subheader {
  padding-left: 8px !important;
}
</style>
