<template>
  <div>
    <v-skeleton-loader v-if="internalLoading" type="text" />
    <v-textarea
      v-else
      :disabled="isEditable"
      :rows="rows"
      :label="label"
      variant="underlined"
      density="compact"
      v-model="textField"
      @update:model-value="onInput"
      auto-grow
    />
  </div>
</template>

<script>
import { watch, ref, toRefs } from "vue"

export default {
  name: "EditableTextArea",
  props: {
    modelValue: {
      type: String,
      default: "",
      required: true,
    },
    rows: {
      type: Number,
      default: 1,
    },
    label: {
      type: String,
      required: true,
    },
    loading: {
      type: Boolean,
      default: false,
    },
  },
  emits: ["update:modelValue"],
  setup(props, { emit }) {
    const { modelValue, loading } = toRefs(props)
    const textField = ref(props.modelValue)
    const internalLoading = ref(props.loading)
    const isEditable = ref(false)

    watch(modelValue, (newValue) => {
      textField.value = newValue
    })

    watch(loading, (newValue) => {
      internalLoading.value = newValue
    })

    const enableEdit = () => {
      isEditable.value = true
    }

    const onInput = (newValue) => {
      if (isEditable.value) {
        emit("update:modelValue", newValue)
      }
    }

    return {
      textField,
      isEditable,
      internalLoading,
      enableEdit,
      onInput,
    }
  },
}
</script>
