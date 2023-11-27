<script setup lang="ts">
import { ref, computed, watchEffect } from "vue"
import Util from "@/util"
import FancyMenu from "@/components/FancyMenu.vue"
import { useRoute } from "vue-router"
import CaseApi from "@/case/api"
import { formatRelativeDate } from "@/filters"

const route = useRoute()

// Define Props
const props = defineProps({
  modelValue: {
    type: Array,
    required: false,
    default: () => [],
  },
})

const events = ref([])

watchEffect(async () => {
  if (props.modelValue.length > 0) {
    events.value = props.modelValue
  } else if (route.params.id) {
    const caseId = parseInt(route.params.id, 10)
    const caseData = await CaseApi.get(caseId)
    events.value = caseData.data.events
  }
})

const showDetails = ref(false)
const exportLoading = ref(false)

const sortedEvents = computed(() => {
  return events.value.slice().sort((a, b) => new Date(a.started_at) - new Date(b.started_at))
})

const exportToCSV = () => {
  exportLoading.value = true
  let items = sortedEvents.value
  // Assuming you want to name the file based on some other data, adjust as needed
  Util.exportCSV(items, "timeline-export.csv")
  exportLoading.value = false
}

const sourceIconMap = {
  "Dispatch Plugin - Ticket Management": {
    icon: "mdi-jira",
    sourceName: "Dispatch",
  },
  "Slack Plugin - Conversation Management": {
    icon: "mdi-slack",
    sourceName: "Dispatch",
  },
  "Dispatch Core App": {
    icon: "mdi-file-document",
    sourceName: "Dispatch",
  },
  "Dispatch Plugin - Participant Resolver": {
    icon: "mdi-account-check",
    sourceName: "Dispatch",
  },
  // Add more mappings as needed...
}

const handleSelection = (selection: string) => {
  if (selection === "Export") {
    exportToCSV()
  }
}

const descriptionMap = {
  "Case created": "created a case",
  "Case ticket created": "created a case ticket",
  "Case participants resolved": "resolved case participants",
  "Case conversation created": "started a case conversation",
  "Conversation added to case": "added conversation to case",
  "Case participants added to conversation.": "added case participants to conversation",
  // Add more mappings as needed...
}

const menu = ref(false)
</script>

<template>
  <v-container class="pl-8 pr-8">
    <v-row justify="end">
      <!-- <v-switch v-model="showDetails" label="Show details" /> -->
      <FancyMenu :options="['Export']" @selection-changed="handleSelection" />
    </v-row>
    <template v-if="sortedEvents && sortedEvents.length">
      <v-timeline density="compact" clipped line-thickness="1">
        <v-timeline-item
          v-for="event in sortedEvents"
          :key="event.id"
          class="mb-4"
          :dot-color="sourceIconMap[event.source]?.icon ? 'transparent' : 'grey'"
          :class="{ 'has-icon': !!sourceIconMap[event.source]?.icon }"
          size="x-small"
        >
          <template v-slot:icon>
            <v-icon size="small" v-if="sourceIconMap[event.source]?.icon">{{
              sourceIconMap[event.source].icon
            }}</v-icon>
          </template>
          <v-row>
            <v-col cols="12">
              <div>
                <span style="font-size: 0.75rem">
                  <b>
                    {{ sourceIconMap[event.source]?.sourceName || event.source }}
                  </b>
                  {{ descriptionMap[event.description] || event.description }} ·
                  {{ formatRelativeDate(event.started_at) }}
                </span>
              </div>
            </v-col>
          </v-row>
        </v-timeline-item>

        <v-timeline-item hide-dot>
          <v-col class="text-right text-caption">(times in UTC)</v-col>
        </v-timeline-item>
      </v-timeline>
    </template>
    <div v-else>
      <v-skeleton-loader
        v-for="(loader, index) in Array(10)"
        :key="index"
        :type="index % 2 === 0 ? 'paragraph' : 'article'"
        max-width="400px"
      ></v-skeleton-loader>
    </div>
  </v-container>
</template>

<style scoped src="@/styles/timeline.css">
.cn-button {
  border-radius: 4px !important;
  font-weight: 500 !important;
  line-height: normal !important;
  border: 1px solid rgb(223, 225, 228) !important;
  box-shadow: rgba(0, 0, 0, 0.09) 0px 1px 4px !important;
  background-color: rgb(255, 255, 255) !important;
  color: rgb(60, 65, 73) !important;
  height: 28px !important;
  padding: 0px 14px !important;
}

.dispatch-side-card {
  backdrop-filter: blur(12px) saturate(190%) contrast(50%) brightness(130%) !important;
  border: 0.5px solid rgb(216, 216, 216) !important;
  border-radius: 8px !important;
  box-shadow: rgba(0, 0, 0, 0.09) 0px 3px 12px !important;
  color: rgb(60, 65, 73) !important;
  opacity: 2 !important;
}
</style>
