<template>
  <div>
    <v-btn variant="plain" :ripple="false" @click="dialog = true">
      <v-icon>{{ lockIcon }}</v-icon>
    </v-btn>

    <v-dialog v-model="dialog" max-width="600px">
      <v-card>
        <v-card-title>Change {{ subjectTitle }} Visibility</v-card-title>
        <v-card-text>
          You are about to change the {{ subjectTitle.toLowerCase() }} visibility from
          <b>{{ visibility }}</b> to <b>{{ toggleVisibility }}</b
          >.
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="updateVisibility">Confirm</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from "vue"
import { useStore } from "vuex"
import CaseApi from "@/case/api"
import IncidentApi from "@/incident/api"

const props = defineProps({
  subjectVisibility: {
    type: String,
    required: true,
  },
  subjectType: {
    type: String,
    required: true,
  },
})

const store = useStore()
const dialog = ref(false)
const visibility = ref(props.subjectVisibility)

const lockIcon = computed(() => (visibility.value === "Open" ? "mdi-lock-open" : "mdi-lock"))

const toggleVisibility = computed(() => (visibility.value === "Open" ? "Restricted" : "Open"))

const subjectTitle = computed(() => (props.subjectType === "incident" ? "Incident" : "Case"))

watch(
  () => props.subjectVisibility,
  (newVal) => {
    visibility.value = newVal
  },
  { immediate: true }
)

async function updateVisibility() {
  const subject = store.state[props.subjectType].selected
  const previousVisibility = visibility.value // Store the previous visibility value

  // Optimistically update the UI
  visibility.value = toggleVisibility.value
  subject.visibility = visibility.value
  dialog.value = false

  try {
    await (props.subjectType === "incident" ? IncidentApi : CaseApi).update(subject.id, subject)
  } catch (e) {
    console.error(`Failed to update ${props.subjectType} visibility`, e)

    // If the API call fails, revert the visibility change and show a toast
    visibility.value = previousVisibility
    store.commit(
      "notification_backend/addBeNotification",
      {
        text: `Failed to update ${props.subjectType} visibility`,
        type: "exception",
      },
      { root: true }
    )
  }
}
</script>
