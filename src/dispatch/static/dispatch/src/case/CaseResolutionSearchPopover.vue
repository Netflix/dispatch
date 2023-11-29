<script setup lang="ts">
import { ref } from "vue"
import type { Ref } from "vue"

import CaseApi from "@/case/api"
import SearchPopover from "@/components/SearchPopover.vue"
import { useStore } from "vuex"

defineProps<{ caseResolution: string }>()

const store = useStore()

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

  await CaseApi.update(caseDetails.id, caseDetails)
}
</script>

<template>
  <SearchPopover
    :items="caseResolutions"
    class="dispatch-button"
    :initialValue="caseResolution || 'Resolution Reason'"
    @item-selected="selectCaseResolution"
    label="Set resolution..."
    :hotkeys="[]"
  >
    <template v-slot:default="{ item }">
      <v-list-item-title class="dispatch-text-title">{{ item }}</v-list-item-title>
    </template>
  </SearchPopover>
</template>

<style lang="scss" scoped>
@import "@/styles/index.scss";
</style>
