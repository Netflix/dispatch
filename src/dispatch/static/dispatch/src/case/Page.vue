<template>
  <div>
    <PageHeader
      :case-id="caseDetails.id"
      :case-description="caseDetails.description"
      :case-name="caseDetails.name"
      :case-visibility="caseDetails.visibility"
      :case-status="caseDetails.status"
      :case-title="caseDetails.title"
      :case-updated-at="caseDetails.updated_at"
      :is-drawer-open="isDrawerOpen"
      :active-tab="activeTab"
      @toggle-drawer="toggleDrawer"
    />
    <CaseAttributesDrawer v-model="caseDetails" :open="isDrawerOpen" />
    <VDivider />
    <div class="container mx-auto px-4">
      <RichEditor
        v-if="activeTab !== 'signals' && activeTab !== 'graph'"
        :content="`<h2>${caseDetails.title}</h2>`"
        class="pl-8 pb-6 pt-6"
        @update:model-value="handleTitleUpdate"
      />
      <RichEditor
        v-if="activeTab !== 'signals' && activeTab !== 'graph'"
        :content="`${caseDetails.description}`"
        class="pl-8 pb-6"
        @update:model-value="handleDescriptionUpdate"
      />
      <CaseStatusSelectGroup
        v-if="activeTab !== 'signals' && activeTab !== 'graph'"
        v-model="caseDetails"
        class="pl-4 pb-8"
      />
      <CaseTabs
        class="pt-8"
        :loading="loading"
        v-model="caseDetails"
        v-model:active-tab="activeTab"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue"
import { useStore } from "vuex"
import { useRoute } from "vue-router"

import { debounce } from "lodash"

import CaseApi from "@/case/api"
import CaseAttributesDrawer from "@/case/CaseAttributesDrawer.vue"
import PageHeader from "@/case//PageHeader.vue"
import CaseTabs from "@/case/CaseTabs.vue"
import RichEditor from "@/components/RichEditor.vue"
import CaseStatusSelectGroup from "@/case/CaseStatusSelectGroup.vue"
import { useSavingState } from "@/composables/useSavingState"

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
  updated_at: null,
  visibility: "",
  conversation: null,
  workflow_instances: null,
}

const caseDetails = ref(caseDefaults)
const loading = ref(false)
const isDrawerOpen = ref(true)
const activeTab = ref("main")
const { setSaving } = useSavingState()

const toggleDrawer = () => {
  isDrawerOpen.value = !isDrawerOpen.value
}

const fetchDetails = async () => {
  const caseName = route.params.name
  loading.value = true

  CaseApi.getAll({
    filter: JSON.stringify([
      { and: [{ model: "Case", field: "name", op: "==", value: caseName }] },
    ]),
  }).then((response) => {
    if (response.data.items.length) {
      // get the full data set
      return CaseApi.get(response.data.items[0].id).then((response) => {
        caseDetails.value = response.data

        // Save the fetched case details to the Vuex store
        store.commit("case_management/SET_SELECTED", response.data)
        loading.value = false
      })
    } else {
      caseDetails.value = caseDefaults
      store.commit(
        "notification_backend/addBeNotification",
        {
          text: `Case '${caseName}' could not be found.`,
          type: "exception",
        },
        { root: true }
      )
    }
    loading.value = false
  })
}

const saveCaseDetails = async () => {
  try {
    setSaving(true)
    await CaseApi.update(caseDetails.value.id, caseDetails.value)
    setSaving(false)
  } catch (e) {
    console.error("Failed to save case details", e)
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

watch(
  () => route.params.name,
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
