<template>
  <v-select
    v-model="caseStatuses"
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
  name: "CaseStatusMultiSelect",

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
      items: ["New", "Triage", "Escalated", "Closed"],
    }
  },

  computed: {
    caseStatuses: {
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
