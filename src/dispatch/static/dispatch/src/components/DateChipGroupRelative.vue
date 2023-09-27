<template>
  <v-chip-group
    v-model="selectedDateTime"
    @update:model-value="submit"
    selected-class="red--text text--accent-4"
    mandatory
  >
    <v-chip v-for="option in options" :key="option.value" :value="option.value">
      {{ option.label }}
    </v-chip>
  </v-chip-group>
</template>

<script>
export default {
  name: "DateChipGroupRelative",
  props: {
    modelValue: {
      type: Number,
      default: 30,
    },
  },
  data() {
    return {
      selectedDateTime: this.modelValue,
      options: [
        { value: 1, label: "Last 24 hours" },
        { value: 3, label: "Last 3 days" },
        { value: 7, label: "Last week" },
        { value: 30, label: "Last month" },
        { value: 365, label: "Last year" },
      ],
    }
  },
  methods: {
    submit() {
      this.$emit("update:modelValue", this.selectedDateTime)
    },
  },
}
</script>
