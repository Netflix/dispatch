<template>
  <v-select
    v-model="incidentStatuses"
    :items="items"
    :menu-props="{ maxHeight: '400' }"
    :label="label"
    multiple
    clearable
    chips
  />
</template>

<script>
import { cloneDeep } from "lodash"
export default {
  name: "IncidentStatusMultiSelect",
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
        return "Statuses"
      },
    },
  },

  data() {
    return {
      items: ["Active", "Stable", "Closed"],
    }
  },

  computed: {
    incidentStatuses: {
      get() {
        return cloneDeep(this.modelValue)
      },
      set(value) {
        this.$emit("update:modelValue", value)
      },
    },
  },
}
</script>
