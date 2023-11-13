<template>
  <v-btn-toggle v-model="toggleExclusive">
    <v-btn class="arrow"> New </v-btn>
    <v-btn> Triaged </v-btn>
    <v-btn> Resolved </v-btn>
    <v-btn> Escalated </v-btn>
  </v-btn-toggle>
</template>

<script>
import { ref } from "vue"

export default {
  name: "CaseToggleButton",
  props: {
    modelValue: {
      type: String,
      default: () => "New",
      required: true,
    },
  },
  setup(props, { emit }) {
    const toggleExclusive = ref(props.modelValue)

    return { toggleExclusive }
  },
}
</script>

<style scoped>
.arrow {
  clip-path: polygon(0% 0%, 95% 0%, 100% 50%, 95% 100%, 0% 100%);
}
</style>
