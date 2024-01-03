<script setup lang="ts">
import { ref, computed, watchEffect } from "vue"
import Util from "@/util"
import DMenu from "@/components/DMenu.vue"
import { useRoute } from "vue-router"
import CaseApi from "@/case/api"
import { formatRelativeDate, formatToUTC } from "@/filters"
import DTooltip from "@/components/DTooltip.vue"

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
</script>

<template>
  <v-container class="pl-8 pr-8">
    <v-row justify="end">
      <!-- <v-switch v-model="showDetails" label="Show details" /> -->
      <DMenu :options="['Export timeline as CSV']" @selection-changed="handleSelection" />
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
          <template #icon>
            <v-icon size="small" v-if="sourceIconMap[event.source]?.icon">
              {{ sourceIconMap[event.source].icon }}
            </v-icon>
          </template>
          <v-row>
            <v-col cols="12">
              <div>
                <span class="dispatch-text-paragraph">
                  <b>
                    {{ sourceIconMap[event.source]?.sourceName || event.source }}
                  </b>
                  {{ descriptionMap[event.description] || event.description }} ·
                  <DTooltip :text="formatToUTC(event.started_at)" hotkeys="">
                    <template #activator="{ tooltip }">
                      <span class="dispatch-text-paragraph" v-bind="tooltip">
                        {{ formatRelativeDate(event.started_at) }}
                      </span>
                    </template>
                  </DTooltip>
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
      />
    </div>
  </v-container>
</template>

<style lang="scss" scoped>
@import "@/styles/index.scss";
@import "@/styles/timeline.css";
</style>
