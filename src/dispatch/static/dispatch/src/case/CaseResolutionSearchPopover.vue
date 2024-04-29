<script setup lang="ts">
import { ref } from "vue"
import type { Ref } from "vue"

import CaseApi from "@/case/api"
import SearchPopover from "@/components/SearchPopover.vue"
import { useSavingState } from "@/composables/useSavingState"
import { useStore } from "vuex"

defineProps<{ caseResolution: string }>()

const store = useStore()
const { setSaving } = useSavingState()
const caseResolutions: Ref<string[]> = ref([
  "False Positive",
  "User Acknowledged",
  "Mitigated",
  "Escalated",
])

const selectCaseResolution = async (caseResolutionName: string) => {
  // Get the case details from the Vuex store
  const caseDetails = store.state.case_management.selected
  caseDetails.resolution_reason = caseResolutionName

  setSaving(true)
  await CaseApi.update(caseDetails.id, caseDetails)
  setSaving(false)
}
</script>

<template>
  <SearchPopover
    :items="caseResolutions"
    class="dispatch-button"
    :initialValue="caseResolution || 'Set resolution reason'"
    @item-selected="selectCaseResolution"
    label="Set resolution..."
    :hotkeys="[]"
  />
</template>
