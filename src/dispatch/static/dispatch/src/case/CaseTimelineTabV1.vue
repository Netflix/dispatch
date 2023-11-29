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
    <template v-if="events && events.length">
      <v-timeline density="compact" clipped>
        <v-timeline-item hide-dot>
          <v-col class="text-right text-caption">(times in UTC)</v-col>
        </v-timeline-item>
        <v-timeline-item
          v-for="event in sortedEvents"
          :key="event.id"
          class="mb-4"
          dot-color="blue"
          size="small"
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
            <v-col class="text-right" cols="5">
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

<script>
import { mapFields } from "vuex-map-fields"
import Util from "@/util"
import { snakeToCamel, formatToUTC, formatToTimeZones } from "@/filters"

export default {
  name: "CaseTimelineTabOld",

  data() {
    return {
      showDetails: false,
      exportLoading: false,
    }
  },

  setup() {
    return { snakeToCamel, formatToUTC, formatToTimeZones }
  },

  computed: {
    ...mapFields("case_management", ["selected.events", "selected.name"]),

    sortedEvents: function () {
      return this.events.slice().sort((a, b) => new Date(a.started_at) - new Date(b.started_at))
    },
  },

  methods: {
    exportToCSV() {
      this.exportLoading = true
      let items = this.sortedEvents
      Util.exportCSV(items, this.name + "-timeline-export.csv")
      this.exportLoading = false
    },
  },
}
</script>

<style scoped src="@/styles/timeline.css" />
