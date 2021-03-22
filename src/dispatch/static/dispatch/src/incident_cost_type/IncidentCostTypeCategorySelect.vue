<template>
  <v-select
    v-model="incidentCostTypeCategories"
    :items="items"
    :menu-props="{ maxHeight: '400' }"
    :label="label"
    hint="FAIR Form of Loss Category"
    clearable
    chips
  />
</template>

<script>
import { cloneDeep } from "lodash"
export default {
  name: "IncidentCostTypeCategorySelect",

  props: {
    value: {
      type: String,
      default: function() {
        return ""
      }
    },
    label: {
      type: String,
      default: function() {
        return "Category"
      }
    }
  },

  data() {
    return {
      items: ["Primary", "Secondary"]
    }
  },

  computed: {
    incidentCostTypeCategories: {
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
