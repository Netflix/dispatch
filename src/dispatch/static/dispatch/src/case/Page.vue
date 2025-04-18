<template>
  <div>
    <PageHeader :case-description="caseDetails.description" :case-genai-analysis="caseDetails.genai_analysis"
      :case-id="caseDetails.id" :case-name="caseDetails.name" :case-status="caseDetails.status"
      :case-title="caseDetails.title" :case-updated-at="caseDetails.updated_at"
      :case-visibility="caseDetails.visibility" :is-drawer-open="isDrawerOpen" :active-tab="activeTab"
      @toggle-drawer="toggleDrawer" />
    <CaseAttributesDrawer v-model="caseDetails" :open="isDrawerOpen" />
    <VDivider />
    <div class="container mx-auto px-4">
      <RichEditor v-if="activeTab !== 'signals' && activeTab !== 'graph'" :content="`<h2>${caseDetails.title}</h2>`"
        class="pl-8 pb-6 pt-6" @update:model-value="handleTitleUpdate" />
      <RichEditor v-if="activeTab !== 'signals' && activeTab !== 'graph'" :content="`${caseDetails.description}`"
        class="pl-8 pb-6" @update:model-value="handleDescriptionUpdate" />
      <GenaiAnalysisDisplay v-if="activeTab !== 'signals' && activeTab !== 'graph'"
        :analysis="caseDetails.genai_analysis" class="pl-8 pb-6" />
      <CaseStatusSelectGroup v-if="activeTab !== 'signals' && activeTab !== 'graph'" v-model="caseDetails"
        class="pl-4 pb-8" />
      <CaseTabs class="pt-8" :loading="loading" v-model="caseDetails" v-model:active-tab="activeTab" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { debounce } from "lodash"
import { ref, watch, computed, onMounted } from "vue"
import { useRoute } from "vue-router"
import { useSavingState } from "@/composables/useSavingState"
import { useStore } from "vuex"

import CaseApi, { caseKeys } from "@/case/api"
import { useUpdateCase } from "@/case/api"
import { queryClient } from "@/query"
import CaseAttributesDrawer from "@/case/CaseAttributesDrawer.vue"
import CaseStatusSelectGroup from "@/case/CaseStatusSelectGroup.vue"
import CaseTabs from "@/case/CaseTabs.vue"
import PageHeader from "@/case/PageHeader.vue"
import RichEditor from "@/components/RichEditor.vue"
import GenaiAnalysisDisplay from "@/components/GenaiAnalysisDisplay.vue"

const route = useRoute()
const store = useStore()

const caseDefaults = {
  assignee: null,
  case_priority: null,
  case_severity: null,
  case_type: null,
  closed_at: null,
  conversation: null,
  description: "",
  documents: [],
  duplicates: [],
  escalated_at: null,
  events: [],
  genai_analysis: null,
  groups: [],
  id: null,
  incidents: [],
  name: null,
  participants: [],
  project: null,
  related: [],
  reported_at: null,
  reporter: null,
  resolution: "",
  resolution_reason: "",
  signal_instances: [],
  status: "New",
  storage: null,
  tags: [],
  ticket: null,
  title: "",
  triage_at: null,
  updated_at: null,
  visibility: "",
  workflow_instances: null,
}

// Use a regular ref for the case name instead of a computed property
const caseName = ref(route.params.name)

// Create a reactive case details object
const caseDetails = ref(caseDefaults)
const loading = ref(false)
const isDrawerOpen = ref(true)
const activeTab = ref("main")
const { setSaving } = useSavingState()

// Watch for route changes and update the caseName
watch(
  () => route.params.name,
  (newName) => {
    if (newName) {
      caseName.value = newName
      fetchCaseDetails() // Fetch new data when route changes
    }
  }
)

// Use a function to fetch case data instead of a hook directly in the component
const fetchCaseDetails = async () => {
  try {
    loading.value = true
    console.log(`Fetching case details for: ${caseName.value}`)

    // Check if we already have a selected case in the store with this name
    const selectedCase = store.state.case_management.selected
    let caseId = null

    // If we have a selected case with the same name, use its ID
    if (selectedCase && selectedCase.name === caseName.value) {
      caseId = selectedCase.id
      console.log(`Found case ID ${caseId} in store for ${caseName.value}`)
    }

    // If we don't have the ID yet, look it up
    if (!caseId) {
      console.log(`Looking up case ID for ${caseName.value}`)
      const response = await CaseApi.getAll({
        filter: JSON.stringify([
          { and: [{ model: "Case", field: "name", op: "==", value: caseName.value }] },
        ]),
      })

      if (!response.data.items.length) {
        store.commit(
          "notification_backend/addBeNotification",
          {
            text: `Case '${caseName.value}' could not be found.`,
            type: "exception",
          },
          { root: true }
        )
        loading.value = false
        return
      }

      caseId = response.data.items[0].id
    }

    // At this point we have the case ID
    console.log(`Using case ID: ${caseId}`)

    // Check all possible cache locations for this case data
    const cachedData =
      queryClient.getQueryData(caseKeys.detail(caseId)) ||
      queryClient.getQueryData(['cases', 'detail', caseId]) ||
      queryClient.getQueryData(['cases', 'byName', caseName.value])

    if (cachedData) {
      console.log(`Using cached data for case ID: ${caseId}`)
      caseDetails.value = cachedData

      // Save to Vuex store for backward compatibility
      store.commit("case_management/SET_SELECTED", cachedData)
      loading.value = false
    } else {
      console.log(`No cache found for case ID: ${caseId}, fetching from API`)
      // Get the full data set using the ID
      const detailResponse = await CaseApi.get(caseId)
      caseDetails.value = detailResponse.data

      // Save to Vuex store for backward compatibility
      store.commit("case_management/SET_SELECTED", detailResponse.data)

      // Store the data in the cache for future use
      queryClient.setQueryData(caseKeys.detail(caseId), detailResponse.data)
    }
  } catch (error) {
    console.error("Error fetching case details:", error)
    store.commit(
      "notification_backend/addBeNotification",
      {
        text: `Error loading case: ${error.message}`,
        type: "exception",
      },
      { root: true }
    )
  } finally {
    loading.value = false
  }
}

// Call fetchCaseDetails when the component is mounted
onMounted(() => {
  fetchCaseDetails()
})

// Use mutation hook for updates
const updateCaseMutation = useUpdateCase()

const toggleDrawer = () => {
  isDrawerOpen.value = !isDrawerOpen.value
}

const saveCaseDetails = async () => {
  try {
    setSaving(true)
    await updateCaseMutation.mutateAsync({
      caseId: caseDetails.value.id,
      caseData: caseDetails.value
    })
    setSaving(false)
  } catch (e) {
    console.error("Failed to save case details", e)
    store.commit(
      "notification_backend/addBeNotification",
      {
        text: `Failed to save case details: ${e.message}`,
        type: "exception",
      },
      { root: true }
    )
  }
}

const debouncedSave = debounce(saveCaseDetails, 1000)

const handleTitleUpdate = (newTitle) => {
  caseDetails.value.title = newTitle
  debouncedSave()
}

const handleDescriptionUpdate = (newDescription) => {
  caseDetails.value.description = newDescription
  debouncedSave()
}
</script>

<style scoped>
.container {
  max-width: 1920px;
  padding-left: 1rem;
  padding-right: 1rem;
  margin-left: auto;
  margin-right: auto;
}
</style>
