<template>
  <v-select
    v-model="selectedPriority"
    :items="items"
    item-title="name"
    :item-props="(item) => ({ subtitle: item.description })"
    :menu-props="{ maxHeight: '400' }"
    label="Priority"
    return-object
    :loading="loading"
    :error-messages="show_error"
    :rules="[is_priority_in_project]"
  />
</template>

<script>
import SearchUtils from "@/search/utils"
import IncidentPriorityApi from "@/incident/priority/api"

export default {
  name: "IncidentPrioritySelect",
  props: {
    modelValue: {
      type: Object,
      default: () => ({}),
    },
    project: {
      type: Object,
      default: null,
    },
    status: {
      type: String,
      default: "",
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
        // If we only have a name (e.g., from URL params), find by name
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
      if (!this.project) return null
      const stablePriority = this.project.stable_priority
      if (!stablePriority) return null
      if (this.status == "Stable" && this.selectedPriority?.name != stablePriority.name) {
        return `Priority must be ${stablePriority.name} for Stable incidents`
      }
      return null
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
          model: "IncidentPriority",
          field: "enabled",
          op: "==",
          value: "true",
        },
      ]

      filterOptions = SearchUtils.createParametersFromTableOptions(
        { ...filterOptions },
        "IncidentPriority",
        enabledFilter
      )

      IncidentPriorityApi.getAll(filterOptions).then((response) => {
        this.items = response.data.items
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
          // Check if we're moving to a valid project (not null)
          if (this.lastProjectId) {
            this.lastProjectId = newProject.id
            this.resetSelection()
            this.fetchData()
          } else {
            // If new project is null/undefined, just update lastProjectId
            this.lastProjectId = null
          }
        }

        this.validatePriority()
      },
      deep: true,
    },
    status() {
      this.validatePriority()
    },
  },

  created() {
    this.fetchData()
  },
}
</script>
