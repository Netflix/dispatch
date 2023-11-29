<template>
  <v-btn class="ml-2" variant="text" icon @click="toggleVisibility">
    <v-icon size="small" v-if="visibility == 'Open'">mdi-lock-open</v-icon>
    <v-icon v-else>mdi-lock</v-icon>
  </v-btn>
  <v-dialog v-model="visibilityDialog" max-width="600">
    <v-card>
      <v-card-title>Update Case Visibility</v-card-title>
      <v-card-text>
        Are you sure you want to change the case visibility from <b>{{ visibility }}</b> to
        <b>{{ newVisibility }}</b>
      </v-card-text>
      <v-btn
        class="ml-6 mb-4"
        size="small"
        color="info"
        elevation="1"
        @click="changeVisibility(newVisibility)"
      >
        Submit
      </v-btn>
    </v-card>
  </v-dialog>
</template>

<script>
import { ref } from "vue"

export default {
  name: "CaseToggleVisibility",
  props: {
    modelValue: {
      type: String,
      default: () => "Open",
      required: true,
    },
  },

  setup(props, { emit }) {
    const visibility = ref(props.modelValue) // default your data accordingly
    const visibilityDialog = ref(false)
    const newVisibility = ref("")

    const toggleVisibility = () => {
      newVisibility.value = visibility.value === "Open" ? "Restricted" : "Open"
      openVisibilityDialog(newVisibility.value)
    }

    const openVisibilityDialog = (newVisibility) => {
      newVisibility.value = newVisibility
      visibilityDialog.value = true
    }

    const changeVisibility = (newVisibility) => {
      visibilityDialog.value = false
      visibility.value = newVisibility
    }

    return {
      visibility,
      visibilityDialog,
      newVisibility,
      toggleVisibility,
      openVisibilityDialog,
      changeVisibility,
    }
  },
}
</script>
