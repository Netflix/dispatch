<template>
  <div>
    <div class="pl-6 pr-8 d-flex justify-space-between align-center">
      <div class="button-group-container">
        <v-btn-toggle
          v-model="tab"
          mandatory
          variant="outlined"
          rounded="lg"
          selected-class="selected-button"
        >
          <v-btn
            class="text-subtitle-2 unselected-button"
            height="24px"
            value="main"
            variant="plain"
            :ripple="false"
          >
            <span class="button-text">Timeline</span>
          </v-btn>
          <v-btn
            class="text-subtitle-2 unselected-button"
            height="24px"
            value="signals"
            variant="plain"
            :ripple="false"
            :disabled="signalInstances?.length === 0"
          >
            <span class="button-text">Alerts</span>
            <v-badge
              v-if="signalInstances?.length"
              inline
              :content="signalInstances?.length"
              class="small-badge"
            />
          </v-btn>
          <v-btn
            class="text-subtitle-2 unselected-button"
            height="24px"
            value="graph"
            variant="plain"
            :ripple="false"
            :disabled="entities?.length === 0"
          >
            <span class="button-text">Graph</span>
            <v-badge v-if="entities?.length" inline :content="entities?.length" />
          </v-btn>
        </v-btn-toggle>
      </div>

      <div>
        <!-- Ticket Button -->
        <DTooltip text="Open case ticket" hotkeys="">
          <template #activator="{ tooltip }">
            <v-btn
              class="text-subtitle-2 font-weight-regular"
              icon="mdi-jira"
              variant="text"
              size="small"
              :disabled="!modelValue.ticket"
              :href="modelValue.ticket && modelValue.ticket.weblink"
              target="_blank"
              v-bind="tooltip"
            />
          </template>
        </DTooltip>

        <!-- Conversation Button -->
        <DTooltip text="Open case conversation" hotkeys="">
          <template #activator="{ tooltip }">
            <v-btn
              class="text-subtitle-2 font-weight-regular"
              icon="mdi-slack"
              variant="text"
              size="small"
              :disabled="!modelValue.conversation"
              :href="modelValue.conversation && modelValue.conversation.weblink"
              target="_blank"
              v-bind="tooltip"
            />
          </template>
        </DTooltip>

        <!-- Document Button -->
        <DTooltip text="Open case document" hotkeys="">
          <template #activator="{ tooltip }">
            <v-btn
              class="text-subtitle-2 font-weight-regular"
              icon="mdi-file-document"
              variant="text"
              size="small"
              :disabled="!modelValue.documents.length"
              :href="modelValue.documents.length && modelValue.documents[0].weblink"
              target="_blank"
              v-bind="tooltip"
            />
          </template>
        </DTooltip>

        <!-- Storage Button -->
        <DTooltip text="Open case storage" hotkeys="">
          <template #activator="{ tooltip }">
            <v-btn
              class="text-subtitle-2 font-weight-regular"
              icon="mdi-folder-google-drive"
              variant="text"
              size="small"
              :disabled="!modelValue.storage"
              :href="modelValue.storage && modelValue.storage.weblink"
              target="_blank"
              v-bind="tooltip"
            />
          </template>
        </DTooltip>
      </div>
    </div>

    <v-divider />

    <v-window v-model="tab">
      <v-window-item value="main" class="tab">
        <case-timeline-tab v-model="events" />
      </v-window-item>
      <v-window-item value="signals" class="tab">
        <case-signal-instance-tab
          :loading="loading"
          v-model="signalInstances"
          :selected-signal-id="selectedSignalId"
        />
      </v-window-item>
      <v-window-item value="graph" class="tab">
        <GraphTab :signal-instances="signalInstances" />
      </v-window-item>
    </v-window>
  </div>
</template>

<script setup>
import { ref, watch, toRefs } from "vue"
import { useRoute, useRouter } from "vue-router"

import GraphTab from "@/case/GraphTab.vue"
import CaseSignalInstanceTab from "@/case/CaseSignalInstanceTab.vue"
import CaseTimelineTab from "@/case/TimelineTab.vue"

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({
      signal_instances: [],
      resources: [],
      entities: [],
      events: [],
    }),
  },
  activeTab: {
    type: String,
    default: "main",
  },
  loading: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(["update:activeTab"])

const { modelValue, loading, activeTab } = toRefs(props)
const tab = ref(activeTab.value)
const signalInstances = ref(modelValue.value.signal_instances)
const resources = ref(modelValue.value.resources)
const entities = ref(modelValue.value.entities)
const events = ref(modelValue.value.events)
const internalLoading = ref(loading.value)

watch(loading, (newValue) => {
  internalLoading.value = newValue
})

watch(modelValue, (newValue) => {
  signalInstances.value = newValue.signal_instances
  resources.value = newValue.resources
  entities.value = newValue.entities
  events.value = newValue.events
})

const route = useRoute()
const router = useRouter()

watch(
  () => tab.value,
  (tabValue) => {
    console.log("Emitting", tabValue)
    emit("update:activeTab", tabValue)
    // ...
  }
)

watch(
  () => tab.value,
  (tabValue) => {
    if (tabValue === "main") {
      router.push({ name: "CasePage", params: { id: route.id } })
    }

    if (tabValue === "signals") {
      router.push({
        name: "SignalDetails",
        params: { signal_id: signalInstances.value[0].raw.id },
      })
    }
  }
)

watch(
  () => route.params,
  (newParams) => {
    const newSignalId = newParams.signal_id
    if (newSignalId) {
      tab.value = "signals"
    }
  },
  { immediate: true, deep: true }
)
</script>

<style scoped>
.v-tab {
  text-transform: initial; /* Keeping the text's original state */
  color: #272727; /* Slightly darker shade of gray for better contrast and readability */
  font-weight: 400; /* Normal text-weight */
  letter-spacing: normal;
  line-height: 1.5; /* Spacing for better readability */
  font-family: "Inter", sans-serif; /* A modern, readable typeface */
}

.tab {
  transition: all 0.2s ease;
}

.button-group-container {
  background-color: rgb(244, 245, 248);
  margin-bottom: 10px;
  border-radius: 8px; /* Adjust as necessary */
  z-index: 1;
  height: 24px !important;

  transform: scale(0.95);
  display: inline-flex; /* Shrink container to content's size */
}

.selected-button {
  background: white !important;
  background-color: white !important;
  color: white !important;
  box-shadow: rgba(0, 0, 0, 0.09) 0px 1px 4px;
  border: 1px solid black !important;
  border-color: rgb(223, 225, 228) !important;
  height: 24px !important;
  border-width: 1px;
  border-radius: 7px !important; /* Adjust the value as necessary */
}

.small-badge {
  transform: scale(0.9);
}

.selected-button .button-text {
  color: rgb(40, 42, 28) !important;
}

.selected-button.v-btn--variant-plain {
  opacity: 1 !important;
}
</style>
