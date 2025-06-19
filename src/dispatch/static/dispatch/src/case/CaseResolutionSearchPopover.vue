<script setup lang="ts">
import { computed } from "vue"

import CaseApi from "@/case/api"
import SearchPopover from "@/components/SearchPopover.vue"
import { useSavingState } from "@/composables/useSavingState"
import { useStore } from "vuex"

defineProps<{ caseResolution: string }>()

const store = useStore()
const { setSaving } = useSavingState()

const caseResolutions = computed(() => store.state.case_management.resolutionReasons)
const caseResolutionTooltips = computed(() => store.state.case_management.resolutionTooltips)

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
    :tooltips="caseResolutionTooltips"
  />
</template>
