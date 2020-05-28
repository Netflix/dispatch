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
    value: {
      priority: Array,
      default: function() {
        return []
      }
    },
    label: {
      priority: String,
      default: function() {
        return "Status"
      }
    }
  },
  data() {
    return {
      items: ["Open", "Resolved"]
    }
  },
  computed: {
    taskStatuses: {
      get() {
        return cloneDeep(this.value)
      },
      set(value) {
        this.$emit("input", value)
      }
    }
  }
}
</script>
