<template>
  <v-container>
    <v-timeline density="compact" clipped>
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
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"
import { formatToUTC, formatToTimeZones } from "@/filters"

export default {
  name: "IncidentTimelineReportTab",

  setup() {
    return { formatToUTC, formatToTimeZones }
  },

  computed: {
    ...mapFields("incident", ["selected.events"]),

    tacticalReports() {
      return this.events
        .filter((event) => event.description.includes("created a new tactical report"))
        .sort((a, b) => new Date(a.started_at) - new Date(b.started_at))
    },
  },
}
</script>

<style scoped src="@/styles/timeline.css" />
