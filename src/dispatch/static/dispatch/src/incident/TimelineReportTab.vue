<template>
  <v-container>
    <div v-if="summary">
      <v-row>
        <v-col>
          <h2 class="text-h6">Incident Summary</h2>
        </v-col>
        <v-col cols="12" class="pa-0">
          <p class="caveat-text">
            This is an AI-generated summary. Please verify the information before relying on it.
          </p>
        </v-col>
        <v-col cols="12">
          <div v-html="incidentSummary" class="summary-paragraph" />
        </v-col>
      </v-row>
      <v-row justify="center">
        <v-btn @click="regenerateSummary(id)" color="success" class="ma-4">Regenerate</v-btn>
      </v-row>
    </div>
    <v-row>
      <v-col>
        <h2 class="text-h6">Tactical Reports</h2>
      </v-col>
    </v-row>
    <div v-if="tacticalReports.length === 0" class="text-center">
      <v-icon size="x-large">mdi-alert-circle-outline</v-icon>
      <p class="text-h6">No tactical reports have been created yet.</p>
    </div>
    <v-timeline v-else density="compact" clipped>
      <v-timeline-item hide-dot>
        <v-row>
          <v-col class="text-right text-caption">(times in UTC)</v-col>
        </v-row>
      </v-timeline-item>
      <v-timeline-item
        v-for="event in tacticalReports"
        :key="event.id"
        :icon="'mdi-text-box-check'"
        class="mb-4"
        dot-color="blue"
      >
        <template #icon>
          <v-icon color="white" />
        </template>
        <v-row justify="space-between">
          <v-col cols="7">
            {{ event.description }}
            <v-card v-if="event.details">
              <v-card-title class="text-subtitle-1">Conditions</v-card-title>
              <v-card-text>{{ event.details.conditions }}</v-card-text>
              <v-card-title class="text-subtitle-1">Actions</v-card-title>
              <v-card-text>{{ event.details.actions }}</v-card-text>
              <v-card-title class="text-subtitle-1">Needs</v-card-title>
              <v-card-text>{{ event.details.needs }}</v-card-text>
            </v-card>
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
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { formatToUTC, formatToTimeZones } from "@/filters"
import { mapActions } from "vuex"
import DOMPurify from "dompurify"

export default {
  name: "IncidentTimelineReportTab",

  setup() {
    return { formatToUTC, formatToTimeZones }
  },

  computed: {
    ...mapFields("incident", ["selected.id", "selected.events", "selected.summary"]),

    tacticalReports() {
      return this.events
        .filter((event) => event.description.includes("created a new tactical report"))
        .sort((a, b) => new Date(a.started_at) - new Date(b.started_at))
    },

    incidentSummary() {
      return DOMPurify.sanitize(this.summary, { ALLOWED_TAGS: [] })
        .split("\n")
        .map((part) => `<p >${part}</p>`)
        .join("")
    },
  },

  methods: {
    ...mapActions("incident", ["regenerateSummary"]),
  },
}
</script>

<style scoped src="@/styles/timeline.css" />
