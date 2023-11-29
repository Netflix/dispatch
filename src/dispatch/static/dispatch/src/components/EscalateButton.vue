<!-- EscalateButton.vue -->
<template>
  <div>
    <v-btn variant="plain" :ripple="false" @click="showDialog">
      <v-icon>mdi-fire</v-icon>
    </v-btn>
    <CaseEscalateDialog />
  </div>
</template>

<script setup lang="ts">
import { useStore } from "vuex"
import CaseEscalateDialog from "@/case/EscalateDialog.vue"

const store = useStore()

const showDialog = () => {
  const caseDetails = store.state.case_management.selected
  store.dispatch("case_management/showEscalateDialog", caseDetails)
}
</script>
