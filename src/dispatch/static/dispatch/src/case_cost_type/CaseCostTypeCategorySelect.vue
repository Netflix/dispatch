<template>
  <v-select
    v-model="caseCostTypeCategories"
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
  name: "CaseCostTypeCategorySelect",

  props: {
    modelValue: {
      type: String,
      default: function () {
        return ""
      },
    },
    label: {
      type: String,
      default: function () {
        return "Category"
      },
    },
  },

  data() {
    return {
      items: ["Primary", "Secondary"],
    }
  },

  computed: {
    caseCostTypeCategories: {
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
