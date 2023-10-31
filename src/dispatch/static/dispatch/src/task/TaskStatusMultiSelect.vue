<template>
  <v-select
    v-model="taskStatuses"
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
  name: "TaskStatusMultiSelect",
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
        return "Status"
      },
    },
    project: {
      type: String,
      required: false,
      default: function () {
        return ""
      },
    },
  },
  data() {
    return {
      items: ["Open", "Resolved"],
    }
  },
  computed: {
    taskStatuses: {
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
