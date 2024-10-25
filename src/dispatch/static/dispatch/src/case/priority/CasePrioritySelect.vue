<template>
  <v-select
    v-model="selectedPriority"
    :items="items"
    item-title="name"
    :menu-props="{ maxHeight: '400' }"
    label="Priority"
    return-object
    :loading="loading"
    :error-messages="show_error"
    :rules="[is_priority_in_project]"
    clearable
  >
    <template #item="data">
      <v-list-item v-bind="data.props" :title="null">
        <v-list-item-title>{{ data.item.raw.name }}</v-list-item-title>
        <v-list-item-subtitle>
          {{ data.item.raw.description }}
        </v-list-item-subtitle>
      </v-list-item>
    </template>
  </v-select>
</template>

<script>
import SearchUtils from "@/search/utils"
import CasePriorityApi from "@/case/priority/api"

export default {
  name: "CasePrioritySelect",
  props: {
    modelValue: {
      type: Object,
      default: () => ({}),
    },
    project: {
      type: Object,
      default: null,
    },
  },

  data() {
    return {
      loading: false,
      items: [],
      error: null,
      lastProjectId: null,
      is_priority_in_project: () => {
        this.validatePriority()
        return this.error
      },
    }
  },

  computed: {
    selectedPriority: {
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
        this.validatePriority()
      },
    },
    show_error() {
      let items_names = this.items.map((item) => item.name)
      let selected_item = this.selectedPriority?.name || ""
      if (items_names.includes(selected_item) || selected_item == "") {
        return null
      }
      return "Not a valid case priority"
    },
  },

  methods: {
    validatePriority() {
      const project_id = this.project?.id || 0
      const in_project = this.selectedPriority?.project?.id == project_id
      if (in_project) {
        this.error = true
      } else {
        this.error = "Only priorities in selected project are allowed"
      }
    },
    fetchData() {
      this.error = null
      this.loading = true

      let filterOptions = {
        sortBy: ["view_order"],
        descending: [false],
      }

      if (this.project) {
        filterOptions = {
          ...filterOptions,
          filters: {
            project: [this.project],
          },
        }
      }

      let enabledFilter = [
        {
          model: "CasePriority",
          field: "enabled",
          op: "==",
          value: "true",
        },
      ]

      filterOptions = SearchUtils.createParametersFromTableOptions(
        { ...filterOptions },
        "CasePriority",
        enabledFilter
      )

      CasePriorityApi.getAll(filterOptions)
        .then((response) => {
          this.items = response.data.items
        })
        .catch((error) => {
          console.error("Error fetching case priorities:", error)
          this.error = "Failed to load case priorities"
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
    project() {
      this.fetchData()
    },
  },

  created() {
    this.fetchData()
  },
}
</script>
