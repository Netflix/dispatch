<template>
  <v-autocomplete
    v-model="assignee"
    :items="items"
    v-model:search="search"
    :menu-props="{ maxHeight: '400' }"
    hide-selected
    :label="label"
    item-title="name"
    multiple
    closable-chips
    chips
    clearable
    return-object
    placeholder="Start typing to search"
    no-filter
    @update:model-value="handleClear"
    :loading="loading"
  >
    <template #no-data>
      <v-list-item v-if="search">
        <v-list-item-title>
          No individuals matching "
          <strong>{{ search }}</strong
          >".
        </v-list-item-title>
      </v-list-item>
    </template>
    <template #item="{ props, item }">
      <v-list-item v-bind="props" :subtitle="item.raw.email" />
    </template>
    <template #chip="data">
      <v-chip v-bind="data.props" pill>
        <template #prepend>
          <v-avatar color="teal" start> {{ initials(data.item.raw.name) }} </v-avatar>
        </template>
        {{ data.item.raw.name }}
      </v-chip>
    </template>
  </v-autocomplete>
</template>

<script>
import IndividualApi from "@/individual/api"
import { initials } from "@/filters"
import { map } from "lodash"
export default {
  name: "AssigneeComboBox",
  props: {
    modelValue: {
      type: Array,
      default: function () {
        return []
      },
    },
    label: {
      type: String,
      default: function () {
        return "Assignee"
      },
    },
  },

  data() {
    return {
      loading: false,
      items: [],
      select: null,
      search: null,
    }
  },

  setup() {
    return { initials }
  },

  computed: {
    assignee: {
      get() {
        return map(this.modelValue, function (item) {
          return item["individual"]
        })
      },
      set(value) {
        let wrapped = map(value, function (item) {
          if (!("individual" in item)) {
            return { individual: item }
          }
          return item
        })
        this.$emit("update:modelValue", wrapped)
      },
    },
  },

  watch: {
    search(val) {
      val && val !== this.select && this.querySelections(val)
    },
    value(val) {
      if (!val) return
      this.items.push.apply(
        this.items,
        map(val, function (item) {
          return item["individual"]
        })
      )
    },
  },

  methods: {
    querySelections(v) {
      this.loading = "error"
      // Simulated ajax query
      IndividualApi.getAll({ q: v }).then((response) => {
        this.items = response.data.items
        this.loading = false
      })
    },
    handleClear() {
      this.search = null
    },
  },

  created() {
    this.error = null
    this.loading = "error"
    IndividualApi.getAll().then((response) => {
      this.items = response.data.items
      this.loading = false
    })
  },
}
</script>
