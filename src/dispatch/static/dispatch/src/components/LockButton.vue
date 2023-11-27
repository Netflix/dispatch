<!-- LockButton.vue -->
<template>
  <div>
    <FancyTooltip text="Change case visibility" :hotkeys="['L']">
      <template v-slot:activator="{ tooltip }">
        <v-btn variant="plain" :ripple="false" v-bind="tooltip" @click="dialog = true">
          <v-icon>{{ lockIcon }}</v-icon>
        </v-btn>
      </template>
    </FancyTooltip>

    <v-dialog v-model="dialog" max-width="600px">
      <v-card>
        <v-card-title>Change Case Visibility</v-card-title>
        <v-card-text>
          You are about to change the case visibility from <b>{{ visibility }}</b> to
          <b>{{ toggleVisibility }}</b
          >.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="updateVisibility">Confirm</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from "vue"
import { useStore } from "vuex"
import FancyTooltip from "@/components/FancyTooltip.vue"
import CaseApi from "@/case/api"

const props = defineProps({
  caseVisibility: {
    type: String,
    required: true,
  },
})

const store = useStore()
const dialog = ref(false)
const visibility = ref(props.caseVisibility)

console.log("Case visibility is", visibility)

watch(
  () => props.caseVisibility,
  (newVal) => {
    visibility.value = newVal
  },
  { immediate: true }
)

async function updateVisibility() {
  const caseDetails = store.state.case_management.selected
  const previousVisibility = visibility.value // Store the previous visibility value

  // Optimistically update the UI
  visibility.value = toggleVisibility.value
  caseDetails.visibility = visibility.value
  dialog.value = false

  try {
    await CaseApi.update(caseDetails.id, caseDetails)
    console.log("Case visibility updated successfully to", visibility.value)
  } catch (e) {
    console.error("Failed to update case visibility", e)

    // If the API call fails, revert the visibility change and show a toast
    visibility.value = previousVisibility
    store.commit(
      "notification_backend/addBeNotification",
      {
        text: "Failed to update case visibility",
        type: "error",
      },
      { root: true }
    )
  }
}

const lockIcon = computed(() => (visibility.value === "Open" ? "mdi-lock-open" : "mdi-lock"))

const toggleVisibility = computed(() => (visibility.value === "Open" ? "Restricted" : "Open"))
</script>
