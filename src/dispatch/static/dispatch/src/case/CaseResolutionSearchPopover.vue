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
    class="dispatch-button-out"
    :initialValue="caseResolution || 'set reason'"
    @item-selected="selectCaseResolution"
    label="Set resolution..."
    :hotkeys="['t']"
  >
    <template v-slot:default="{ item }">
      <v-list-item-title class="item-title-font">{{ item }}</v-list-item-title>
    </template>
  </SearchPopover>
</template>

<style scoped>
.item-title-font {
  font-size: 13px !important;
}

.dispatch-button-out {
  text-transform: none !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  margin: 0px !important;
  font-weight: 500px !important;
  line-height: normal !important;
  transition-property: border, background-color, color, opacity !important;
  transition-duration: 0.15s !important;
  user-select: none !important;
  box-shadow: rgba(0, 0, 0, 0.09) 0px 1px 4px !important;
  background-color: rgb(255, 255, 255) !important;
  border: 1px solid rgb(223, 225, 228) !important;
  border-radius: 4px !important;
  color: rgb(60, 65, 73) !important;
  min-width: 28px !important;
  height: 28px !important;
  padding: 0px 14px !important;
  font-size: 0.75rem !important;
}
</style>
