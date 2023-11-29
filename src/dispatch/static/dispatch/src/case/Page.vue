<template>
  <div>
    <PageHeader
      :case-name="caseDetails.name"
      :case-visibility="caseDetails.visibility"
      :case-status="caseDetails.status"
      :is-drawer-open="isDrawerOpen"
      @toggle-drawer="toggleDrawer"
    />
    <CaseAttributesDrawer v-model="caseDetails" :open="isDrawerOpen" />
    <VDivider />
    <div class="container mx-auto px-4">
      <RichEditor
        :title="true"
        v-model="caseDetails.title"
        class="pl-8 pb-6 pt-6"
        @update:model-value="handleTitleUpdate"
      />
      <RichEditor
        :description="true"
        v-model="caseDetails.description"
        class="pl-8 pb-6"
        @update:model-value="handleDescriptionUpdate"
      />
      <CaseStatusSelectGroup v-model="caseDetails" class="pl-4 pb-8" />
      <CaseTabs :loading="loading" v-model="caseDetails" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue"
import { useStore } from "vuex"

import { useRoute } from "vue-router"
import CaseApi from "@/case/api"
import CaseAttributesDrawer from "@/case/CaseAttributesDrawer.vue"
import PageHeader from "@/case//PageHeader.vue"
import CaseTabs from "@/case/CaseTabs.vue"
import RichEditor from "@/components/RichEditor.vue"
import CaseStatusSelectGroup from "@/case/CaseStatusSelectGroup.vue"

const route = useRoute()
const store = useStore()

const caseDefaults = {
  status: "New",
  assignee: null,
  case_priority: null,
  case_severity: null,
  case_type: null,
  closed_at: null,
  description: "",
  documents: [],
  duplicates: [],
  escalated_at: null,
  participants: [],
  events: [],
  groups: [],
  id: null,
  incidents: [],
  name: null,
  project: null,
  related: [],
  reporter: null,
  reported_at: null,
  resolution_reason: "",
  resolution: "",
  title: "",
  signal_instances: [],
  storage: null,
  tags: [],
  ticket: null,
  triage_at: null,
  visibility: "",
  conversation: null,
  workflow_instances: null,
}

const caseDetails = ref(caseDefaults)
const loading = ref(false)
const isDrawerOpen = ref(true)

const toggleDrawer = () => {
  isDrawerOpen.value = !isDrawerOpen.value
}

const fetchDetails = async () => {
  const caseId = parseInt(route.params.id, 10)
  loading.value = true
  try {
    // get the full data set
    CaseApi.get(caseId).then((response) => {
      caseDetails.value = response.data

      // Save the fetched case details to the Vuex store
      store.commit("case_management/SET_SELECTED", response.data)
    })
  } catch (e) {
    console.error("Failed to fetch case details", e)
    caseDetails.value = caseDefaults
    loading.value = false
  }
}

const handleTitleUpdate = (newTitle) => {
  caseDetails.value.title = newTitle
  saveCaseDetails()
}

const handleDescriptionUpdate = (newDescription) => {
  caseDetails.value.description = newDescription
  saveCaseDetails()
}

const saveCaseDetails = async () => {
  try {
    await CaseApi.update(caseDetails.value.id, caseDetails.value)
  } catch (e) {
    console.error("Failed to save case details", e)
  }
}

watch(
  () => route.params.id,
  (newName, oldName) => {
    if (newName !== oldName) {
      fetchDetails()
    }
  },
  { immediate: true }
)
</script>

<style scoped>
.container {
  max-width: 1920px; /* for example */
  padding-left: 1rem;
  padding-right: 1rem;
  margin-left: auto;
  margin-right: auto;
}
</style>
