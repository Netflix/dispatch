<script setup lang="ts">
import { ref, computed } from "vue"
import Util from "@/util"
import { snakeToCamel, formatToUTC, formatToTimeZones } from "@/filters"

// Define Props
const props = defineProps({
  modelValue: {
    type: Array,
    required: true,
  },
})

const showDetails = ref(false)
const exportLoading = ref(false)

console.log("The timeline got", props.modelValue)

const sortedEvents = computed(() => {
  return props.modelValue.slice().sort((a, b) => new Date(a.started_at) - new Date(b.started_at))
})

const exportToCSV = () => {
  exportLoading.value = true
  let items = sortedEvents.value
  // Assuming you want to name the file based on some other data, adjust as needed
  Util.exportCSV(items, "timeline-export.csv")
  exportLoading.value = false
}

const getAvatarGradient = (participant: string) => {
  let hash = 5381
  for (let i = 0; i < participant.length; i++) {
    hash = ((hash << 5) + hash) ^ participant.charCodeAt(i) // Using XOR operator for better distribution
  }

  const hue = Math.abs(hash) % 360 // Ensure hue is a positive number
  const fromColor = `hsl(${hue}, 95%, 50%)`
  const toColor = `hsl(${(hue + 120) % 360}, 95%, 50%)` // Getting triadic color by adding 120 to hue

  return `linear-gradient(${fromColor}, ${toColor})`
}
</script>

<template>
  <v-container>
    <v-row justify="end">
      <v-switch v-model="showDetails" label="Show details" />
      <v-btn
        color="secondary"
        class="ml-2 mr-2 mt-3"
        @click="exportToCSV()"
        :loading="exportLoading"
      >
        Export
      </v-btn>
    </v-row>
    <template v-if="sortedEvents && sortedEvents.length">
      <v-timeline density="compact" clipped line-thickness="1">
        <v-timeline-item class="mb-12" size="x-small">
          <template v-slot:icon>
            <v-avatar size="18px" :style="{ background: getAvatarGradient('Will Sheldon') }">
            </v-avatar>
          </template>
          <v-card class="rounded-lg dispatch-side-card">
            <v-textarea
              name="input-7-1"
              variant="text"
              label="Label"
              auto-grow
              rows="4"
              row-height="30"
              model-value="The Woodman set to work at once, and so sharp was his axe that the tree was soon chopped nearly through."
            >
            </v-textarea>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn
                @click="comment"
                class="ma-2 text-subtitle-2 font-weight-regular cn-button"
                elevation="1"
              >
                Comment
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-timeline-item>
        <v-timeline-item hide-dot>
          <v-col class="text-right text-caption">(times in UTC)</v-col>
        </v-timeline-item>
        <v-timeline-item
          v-for="event in sortedEvents"
          :key="event.id"
          class="mb-4"
          dot-color="blue"
          size="x-small"
        >
          <v-row justify="space-between">
            <v-col cols="7">
              {{ event.description }}
              <transition-group name="slide" v-if="showDetails">
                <template v-for="(value, key) in event.details" :key="key">
                  <v-card>
                    <v-card-title class="text-subtitle-1">
                      {{ snakeToCamel(key) }}
                    </v-card-title>
                    <v-card-text>{{ value }}</v-card-text>
                  </v-card>
                </template>
              </transition-group>
              <div class="text-caption">
                {{ event.source }}
              </div>
            </v-col>
            <v-col class="text-right" cols="4">
              <v-tooltip location="bottom">
                <template #activator="{ props }">
                  <span v-bind="props" class="wavy-underline">{{
                    formatToUTC(event.started_at)
                  }}</span>
                </template>
                <span class="pre-formatted">{{ formatToTimeZones(event.started_at) }}</span>
              </v-tooltip>
            </v-col>
          </v-row>
        </v-timeline-item>
      </v-timeline>
    </template>
    <div v-else>
      <p class="text-center">No timeline data available.</p>
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
