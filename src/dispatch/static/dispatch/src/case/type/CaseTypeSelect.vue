<template>
  <v-select
    v-model="case_type"
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
    :rules="[is_type_in_project]"
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
    <v-col cols="12">
      <p>Conversation Target: {{ conversation_target }}</p>
    </v-col>
  </v-select>
</template>

<script>
import { cloneDeep } from "lodash"
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
    hint: {
      type: String,
      default: () => "Case Type to associate",
    },
    label: {
      type: String,
      default: () => "Case Type",
    },
  },

  data() {
    return {
      conversation_target: null,
      loading: false,
      items: [],
      search: null,
      more: false,
      numItems: 40,
      error: null,
      categories: [],
      selectedCaseType: null,
      is_type_in_project: () => {
        this.validateType()
        return this.error
      },
    }
  },

  computed: {
    case_type: {
      get() {
        return this.selectedCaseType || this.modelValue
      },
      set(value) {
        this.selectedCaseType = value
        this.$emit("update:modelValue", value)
        this.validateType()
      },
    },
    show_error() {
      let items_names = this.items.map((item) => item.name)
      let selected_item = this.case_type?.name || ""
      if (items_names.includes(selected_item) || selected_item == "") {
        return null
      }
      return "Not a valid case type"
    },
  },

  methods: {
    loadMore() {
      this.numItems = this.numItems + 5
      this.fetchData()
    },
    validateType() {
      let in_project
      if (this.project?.name) {
        let project_name = this.project?.name || ""
        in_project = this.case_type?.project?.name == project_name
      } else {
        let project_id = this.project?.id || 0
        in_project = this.case_type?.project?.id == project_id
      }

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

      CaseTypeApi.getAll(filterOptions).then((response) => {
        // re-sort items by oncall service
        this.items = []
        this.categories = []
        let new_items = {}
        response.data.items.forEach((item) => {
          let category = "Team: " + (item.oncall_service?.name || "None")
          new_items[category] = new_items[category] || []
          new_items[category].push(item)
        })
        let keys = Object.keys(new_items)
        // ensure Team: None is always at the end
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

        this.total = response.data.total
        this.loading = false

        if (this.items.length < this.total) {
          this.more = true
        } else {
          this.more = false
        }

        // Set the selected case type if it exists in the fetched items
        if (this.modelValue && this.modelValue.id) {
          const selectedItem = this.items.find((item) => item.id === this.modelValue.id)
          if (selectedItem) {
            this.selectedCaseType = selectedItem
          }
        }
      })
    },
  },

  watch: {
    search(val) {
      val && val !== this.select && this.fetchData()
    },
    modelValue: {
      handler(newValue) {
        if (newValue && newValue.id) {
          const selectedItem = this.items.find((item) => item.id === newValue.id)
          if (selectedItem) {
            this.selectedCaseType = selectedItem
          }
        } else {
          this.selectedCaseType = null
        }
      },
      immediate: true,
    },
    case_type(newCaseType) {
      if (newCaseType) {
        this.conversation_target = newCaseType.conversation_target
      } else {
        this.conversation_target = null
      }
    },
  },

  created() {
    this.fetchData()
    this.$watch(
      (vm) => [vm.project],
      () => {
        this.fetchData()
        this.validateType()
        this.$emit("update:modelValue", this.case_type)
      }
    )
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
