<template>
  <v-container>
    <v-row justify="end">
      <v-switch v-model="showDetails" label="Show details"></v-switch>
    </v-row>
    <v-timeline v-if="events.length" dense clipped>
      <v-timeline-item
        v-for="event in sortedEvents"
        v-bind:key="event.id"
        class="mb-4"
        color="blue"
        small
      >
        <v-row justify="space-between">
          <v-col cols="7">
            {{ event.description }}
            <transition-group name="slide" v-if="showDetails">
              <template v-for="(value, key) in event.details">
                <v-card flat="true" v-bind:key="key">
                  <v-card-title class="subtitle-1">{{ key | snakeToCamel }}</v-card-title>
                  <v-card-text>{{ value }}</v-card-text>
                </v-card>
              </template>
            </transition-group>
            <div class="caption">{{ event.source }}</div>
          </v-col>
          <v-col class="text-right" cols="5">{{ event.started_at | formatDate }}</v-col>
        </v-row>
      </v-timeline-item>
    </v-timeline>
    <div v-else>
      <p class="text-center">
        No timeline data available.
      </p>
    </div>
  </v-container>
</template>

<script>
import { mapFields } from "vuex-map-fields"

export default {
  name: "IncidentTimelineTab",

  data() {
    return {
      showDetails: false
    }
  },

  computed: {
    ...mapFields("incident", ["selected.events"]),

    sortedEvents: function() {
      return this.events.slice().sort((a, b) => new Date(a.started_at) - new Date(b.started_at))
    }
  }
}
</script>
