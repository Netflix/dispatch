<!-- EscalateButton.vue -->
<template>
  <div>
    <FancyTooltip text="Escalate case" :hotkeys="['E']">
      <template #activator="{ tooltip }">
        <v-btn variant="plain" :ripple="false" v-bind="tooltip" @click="showDialog">
          <v-icon>mdi-fire</v-icon>
        </v-btn>
      </template>
    </FancyTooltip>
    <CaseEscalateDialog />
  </div>
</template>

<script setup lang="ts">
import { useStore } from "vuex"
import FancyTooltip from "@/components/FancyTooltip.vue"
import CaseEscalateDialog from "@/case/EscalateDialog.vue"

const store = useStore()

const showDialog = () => {
  const caseDetails = store.state.case_management.selected
  store.dispatch("case_management/showEscalateDialog", caseDetails)
}
</script>
