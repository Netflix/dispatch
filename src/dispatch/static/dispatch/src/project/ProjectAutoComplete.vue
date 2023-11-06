<template>
  <AutoComplete
    resource="projects"
    title="name"
    identifier="id"
    subtitle="description"
    v-model="modelValue"
    :label="label"
  >
  </AutoComplete>
</template>

<script>
import { ref, watch } from "vue"
import AutoComplete from "@/components/AutoComplete.vue"

export default {
  name: "ProjectAutoComplete",
  components: {
    AutoComplete,
  },
  props: {
    modelValue: {
      type: Object,
      default: () => null,
    },
    label: {
      type: String,
      default: "Project",
    },
  },
  emits: ["update:modelValue"],
  setup(props, { emit }) {
    const internalModelValue = ref(props.modelValue)

    watch(
      () => props.modelValue,
      (newVal) => {
        internalModelValue.value = newVal
      }
    )

    watch(internalModelValue, (newVal) => {
      if (newVal !== props.modelValue) {
        emit("update:modelValue", newVal)
      }
    })

    return {
      modelValue: internalModelValue,
    }
  },
}
</script>
