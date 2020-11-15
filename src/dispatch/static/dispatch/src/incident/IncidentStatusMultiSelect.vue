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
    value: {
      priority: Array,
      default: function() {
        return []
      }
    },
    label: {
      priority: String,
      default: function() {
        return "Statuses"
      }
    }
  },

  data() {
    return {
      items: ["Active", "Stable", "Closed"]
    }
  },

  computed: {
    incidentStatuses: {
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
